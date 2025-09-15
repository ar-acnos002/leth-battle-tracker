import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random

# Refresh every 5 seconds
st_autorefresh(interval=500, key="auto_refresh")


# ---- Config ----
MAX_HEALTH = 20
MAX_MANA = 10

# Hide the header, "Manage App" button, and "Made with Streamlit" footer
st.markdown(
    """
    <style>
    /* Hide the hamburger menu */
    #MainMenu {visibility: hidden;}
    
    /* Hide the footer */
    footer {visibility: hidden;}
    
    /* Hide the header */
    header {visibility: hidden;}

    /* Hide the "Deploy" button (useful for local testing) */
    .stDeployButton {display: none;}

    /* Target the "Manage App" button in the Community Cloud */
    .embeddedAppMetaInfoBar_container__DxxL1 {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(page_title="Dead by D&D", page_icon="⚔️", layout="wide")


# ---- Shared Global State (cache_resource) ----
@st.cache_resource
def get_shared_state():
    return {
        "party": [
            {"name": "Xharis Paridion", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Vaelor Grimvier", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Aethos", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Jetta Yu", "health": MAX_HEALTH, "mana": MAX_MANA},
        ],
        "extra_party": [],
        "enemies": [],
        "battle_active": False,
        "turn_number": 1,
    }


state = get_shared_state()


# ---- Helpers ----
def clamp(value, lo, hi):
    return max(lo, min(value, hi))


def update_party_health(idx, delta):
    all_members = state["party"] + state["extra_party"]
    all_members[idx]["health"] = clamp(
        all_members[idx]["health"] + delta, 0, MAX_HEALTH
    )


def update_party_mana(idx, delta):
    all_members = state["party"] + state["extra_party"]
    all_members[idx]["mana"] = clamp(all_members[idx]["mana"] + delta, 0, MAX_MANA)


def remove_party_member(idx):
    if idx >= len(state["party"]):
        del state["extra_party"][idx - len(state["party"])]


def update_enemy_health(idx, delta):
    state["enemies"][idx]["health"] = clamp(
        state["enemies"][idx]["health"] + delta, 0, MAX_HEALTH
    )


def update_enemy_mana(idx, delta):
    state["enemies"][idx]["mana"] = clamp(
        state["enemies"][idx]["mana"] + delta, 0, MAX_MANA
    )


def add_party_member():
    state["extra_party"].append(
        {
            "name": f"Extra Member {len(state['extra_party'])+1}",
            "health": MAX_HEALTH,
            "mana": MAX_MANA,
        }
    )


def add_enemy():
    state["enemies"].append(
        {
            "name": f"Enemy {len(state['enemies'])+1}",
            "health": MAX_HEALTH,
            "mana": MAX_MANA,
        }
    )


def remove_enemy(idx):
    del state["enemies"][idx]


def long_rest():
    for member in state["party"] + state["extra_party"]:
        member["health"] = MAX_HEALTH
        member["mana"] = MAX_MANA
        member["latest_roll"] = ""
        member["roll_count"] = 0


def start_battle():
    state["battle_active"] = True
    state["turn_number"] = 1


def end_battle():
    state["battle_active"] = False
    state["turn_number"] = 1


def next_turn():
    state["turn_number"] += 1
    if state["turn_number"] % 2 > 0:
        for member in state["party"] + state["extra_party"]:
            member["health"] = min(member["health"] + 1, MAX_HEALTH)
            member["mana"] = min(member["mana"] + 1, MAX_MANA)

    if state["turn_number"] % 2 == 0:
        for enemy in state["enemies"]:
            enemy["health"] = min(enemy["health"] + 1, MAX_HEALTH)
            enemy["mana"] = min(enemy["mana"] + 1, MAX_MANA)


def roll_dice(num_dice, sides=6):
    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(rolls)
    return total


# ---- UI ----
st.markdown(
    """
    <h2 style='text-align: center; margin-top: -105px; font-family: "Gill Sans", sans-serif; font-style: bold;'>Dead by D&D</h2>
    """,
    unsafe_allow_html=True,
)

party_col, enemy_col = st.columns(2, gap="large")

# ----- Party UI -----
with party_col:
    if st.button("Long Rest", use_container_width=True):
        long_rest()
        st.rerun()

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Party Members")
    with col2:
        if st.button("+ Add Party Member", use_container_width=True):
            add_party_member()
            st.rerun()

    all_members = state["party"] + state["extra_party"]
    base_len = len(state["party"])

    for i, member in enumerate(all_members):
        with st.container(border=True):
            member["name"] = st.text_input(
                "Name", value=member["name"], key=f"party_name_{i}"
            )

            c1, c2, c3, c_sp, c4, c5, c6 = st.columns(
                [1.2, 2.4, 1.2, 0.6, 1.2, 2.4, 1.2]
            )

            with c1:
                if st.button("➖", key=f"p_h_dec_{i}", use_container_width=True):
                    update_party_health(i, -1)
                    st.rerun()
            with c2:
                st.markdown(f"**Health:** {member['health']} / {MAX_HEALTH}")
            with c3:
                if st.button("➕", key=f"p_h_inc_{i}", use_container_width=True):
                    update_party_health(i, 1)
                    st.rerun()

            with c4:
                if st.button("➖", key=f"p_m_dec_{i}", use_container_width=True):
                    update_party_mana(i, -1)
                    st.rerun()
            with c5:
                st.markdown(f"**Mana:** {member['mana']} / {MAX_MANA}")
            with c6:
                if st.button("➕", key=f"p_m_inc_{i}", use_container_width=True):
                    update_party_mana(i, 1)
                    st.rerun()

            if i >= base_len:
                if st.button("Remove", key=f"p_rm_{i}"):
                    remove_party_member(i)
                    st.rerun()

            # ---- Dice Rolling Section ----
            if "latest_roll" not in member:
                member["latest_roll"] = ""
            if "roll_count" not in member:
                member["roll_count"] = 0

            d1, d2, d3, d4 = st.columns([2, 2, 2, 4])
            with d1:
                if st.button("2D6", key=f"p_roll2_{i}", use_container_width=True):
                    total = roll_dice(2)
                    member["roll_count"] += 1
                    member["latest_roll"] = f"Roll #{member['roll_count']}: {total}"
                    st.rerun()
            with d2:
                if st.button("4D6", key=f"p_roll4_{i}", use_container_width=True):
                    total = roll_dice(4)
                    member["roll_count"] += 1
                    member["latest_roll"] = f"Roll #{member['roll_count']}: {total}"
                    st.rerun()
            with d3:
                if st.button("6D6", key=f"p_roll6_{i}", use_container_width=True):
                    total = roll_dice(6)
                    member["roll_count"] += 1
                    member["latest_roll"] = f"Roll #{member['roll_count']}: {total}"
                    st.rerun()
            with d4:
                st.text_input(
                    "Roll",
                    value=member["latest_roll"],
                    key=f"p_rolltxt_{i}",
                    disabled=True,
                    label_visibility="collapsed",
                )

# ----- Enemies UI -----
with enemy_col:
    if not state["battle_active"]:
        if st.button("Start Battle", use_container_width=True):
            start_battle()
            st.rerun()
    else:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_a:
            if st.button("End Battle", use_container_width=True):
                end_battle()
                st.rerun()
        with col_b:
            st.markdown(f"**Turn: {state['turn_number']}**")
        with col_c:
            if st.button("Next Turn", use_container_width=True):
                next_turn()
                st.rerun()

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Enemies")
    with col2:
        if st.button("+ Add Enemy", use_container_width=True):
            add_enemy()
            st.rerun()

    for i, enemy in enumerate(state["enemies"]):
        with st.container(border=True):
            enemy["name"] = st.text_input(
                "Name", value=enemy["name"], key=f"enemy_name_{i}"
            )

            c1, c2, c3, c_sp, c4, c5, c6 = st.columns(
                [1.2, 2.4, 1.2, 0.6, 1.2, 2.4, 1.2]
            )

            with c1:
                if st.button("➖", key=f"e_h_dec_{i}", use_container_width=True):
                    update_enemy_health(i, -1)
                    st.rerun()
            with c2:
                st.markdown(f"**Health:** {enemy['health']} / {MAX_HEALTH}")
            with c3:
                if st.button("➕", key=f"e_h_inc_{i}", use_container_width=True):
                    update_enemy_health(i, 1)
                    st.rerun()

            with c4:
                if st.button("➖", key=f"e_m_dec_{i}", use_container_width=True):
                    update_enemy_mana(i, -1)
                    st.rerun()
            with c5:
                st.markdown(f"**Mana:** {enemy['mana']} / {MAX_MANA}")
            with c6:
                if st.button("➕", key=f"e_m_inc_{i}", use_container_width=True):
                    update_enemy_mana(i, 1)
                    st.rerun()

            if st.button("Remove", key=f"e_rm_{i}"):
                remove_enemy(i)
                st.rerun()
