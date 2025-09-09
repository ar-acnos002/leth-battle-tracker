import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Refresh every 5 seconds
st_autorefresh(interval=2000, key="auto_refresh")


# ---- Config ----
MAX_HEALTH = 20
MAX_MANA = 10

st.set_page_config(page_title="TTRPG Battle Tracker", layout="wide")


# ---- Shared Global State (Singleton) ----
@st.cache_resource
def get_shared_state():
    return {
        "party": [
            {"name": "Xharis", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Vaelor", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Aethos", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Jetta", "health": MAX_HEALTH, "mana": MAX_MANA},
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


def start_battle():
    state["battle_active"] = True
    state["turn_number"] = 1


def end_battle():
    state["battle_active"] = False
    state["turn_number"] = 1


def next_turn():
    state["turn_number"] += 1
    for member in state["party"] + state["extra_party"]:
        member["health"] = min(member["health"] + 1, MAX_HEALTH)
        member["mana"] = min(member["mana"] + 1, MAX_MANA)


# ---- UI ----
st.markdown(
    "<h1 style='text-align: center; margin-bottom: 50px;'>TTRPG Battle Tracker</h1>",
    unsafe_allow_html=True,
)

party_col, enemy_col = st.columns(2, gap="large")

# ----- Party UI -----
with party_col:
    if st.button("Long Rest", use_container_width=True):
        long_rest()
        st.rerun()

    st.subheader("Party Members")
    if st.button("+ Add Party Member"):
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

    st.subheader("Enemies")
    if st.button("+ Add Enemy"):
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
