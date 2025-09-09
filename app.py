import streamlit as st

# ---- Config ----
MAX_HEALTH = 20
MAX_MANA = 10

st.set_page_config(page_title="TTRPG Battle Tracker", layout="wide")


# ---- State init ----
def init_state():
    if "base_party_members" not in st.session_state:
        st.session_state.base_party_members = [
            {"name": "Xharis", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Vaelor", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Aethos", "health": MAX_HEALTH, "mana": MAX_MANA},
            {"name": "Jetta", "health": MAX_HEALTH, "mana": MAX_MANA},
        ]
    if "extra_party_members" not in st.session_state:
        st.session_state.extra_party_members = []
    if "enemies" not in st.session_state:
        st.session_state.enemies = []


init_state()


# ---- Helpers ----
def clamp(value, lo, hi):
    return max(lo, min(value, hi))


def update_party_health(idx, delta):
    all_members = (
        st.session_state.base_party_members + st.session_state.extra_party_members
    )
    all_members[idx]["health"] = clamp(
        all_members[idx]["health"] + delta, 0, MAX_HEALTH
    )


def update_party_mana(idx, delta):
    all_members = (
        st.session_state.base_party_members + st.session_state.extra_party_members
    )
    all_members[idx]["mana"] = clamp(all_members[idx]["mana"] + delta, 0, MAX_MANA)


def remove_party_member(idx):
    base_len = len(st.session_state.base_party_members)
    if idx >= base_len:
        del st.session_state.extra_party_members[idx - base_len]


def update_enemy_health(idx, delta):
    st.session_state.enemies[idx]["health"] = clamp(
        st.session_state.enemies[idx]["health"] + delta, 0, MAX_HEALTH
    )


def update_enemy_mana(idx, delta):
    st.session_state.enemies[idx]["mana"] = clamp(
        st.session_state.enemies[idx]["mana"] + delta, 0, MAX_MANA
    )


def add_party_member():
    st.session_state.extra_party_members.append(
        {
            "name": f"Extra Member {len(st.session_state.extra_party_members) + 1}",
            "health": MAX_HEALTH,
            "mana": MAX_MANA,
        }
    )


def add_enemy():
    st.session_state.enemies.append(
        {
            "name": f"Enemy {len(st.session_state.enemies) + 1}",
            "health": MAX_HEALTH,
            "mana": MAX_MANA,
        }
    )


def remove_enemy(idx):
    del st.session_state.enemies[idx]


# ---- UI ----
st.markdown(
    "<h1 style='text-align: center; margin-bottom: 100px;'>TTRPG Battle Tracker</h1>",
    unsafe_allow_html=True,
)


# ---- Battle Controls ----
def init_battle_state():
    if "battle_active" not in st.session_state:
        st.session_state.battle_active = False
    if "turn_number" not in st.session_state:
        st.session_state.turn_number = 1  # always start at 1


init_battle_state()


def start_battle():
    st.session_state.battle_active = True


def end_battle():
    st.session_state.battle_active = False
    st.session_state.turn_number = 1


def next_turn():
    st.session_state.turn_number += 1
    # recover health and mana for all party members
    for member in (
        st.session_state.base_party_members + st.session_state.extra_party_members
    ):
        member["health"] = min(member["health"] + 1, MAX_HEALTH)
        member["mana"] = min(member["mana"] + 1, MAX_MANA)


party_col, enemy_col = st.columns(2, gap="large")


# ---- Party Reset ----
def long_rest():
    for member in (
        st.session_state.base_party_members + st.session_state.extra_party_members
    ):
        member["health"] = MAX_HEALTH
        member["mana"] = MAX_MANA


# ----- Party UI -----
with party_col:
    # Long Rest button
    st.button("Long Rest", use_container_width=True, on_click=long_rest)

    st.subheader("Party Members")
    st.button("+ Add Party Member", on_click=add_party_member)

    all_members = (
        st.session_state.base_party_members + st.session_state.extra_party_members
    )
    base_len = len(st.session_state.base_party_members)

    for i, member in enumerate(all_members):
        with st.container(border=True):
            # Editable name
            member["name"] = st.text_input(
                "Name", value=member["name"], key=f"party_name_{i}"
            )

            c1, c2, c3, c_sp, c4, c5, c6 = st.columns(
                [1.2, 2.4, 1.2, 0.6, 1.2, 2.4, 1.2]
            )

            with c1:
                st.button(
                    "➖",
                    key=f"p_h_dec_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_party_health(idx, -1),
                )
            with c2:
                st.markdown(f"**Health:** {member['health']} / {MAX_HEALTH}")
            with c3:
                st.button(
                    "➕",
                    key=f"p_h_inc_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_party_health(idx, 1),
                )

            with c4:
                st.button(
                    "➖",
                    key=f"p_m_dec_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_party_mana(idx, -1),
                )
            with c5:
                st.markdown(f"**Mana:** {member['mana']} / {MAX_MANA}")
            with c6:
                st.button(
                    "➕",
                    key=f"p_m_inc_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_party_mana(idx, 1),
                )

            if i >= base_len:
                if st.button("Remove", key=f"p_rm_{i}"):
                    remove_party_member(i)
                    st.rerun()

# ----- Enemies UI -----
with enemy_col:
    if not st.session_state.battle_active:
        st.button("Start Battle", use_container_width=True, on_click=start_battle)
    else:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_a:
            st.button("End Battle", use_container_width=True, on_click=end_battle)
        with col_b:
            st.markdown(
                f"**Turn: {st.session_state.turn_number}**", unsafe_allow_html=True
            )
        with col_c:
            st.button("Next Turn", use_container_width=True, on_click=next_turn)

    st.subheader("Enemies")
    st.button("+ Add Enemy", on_click=add_enemy)

    for i, enemy in enumerate(st.session_state.enemies):
        with st.container(border=True):
            enemy["name"] = st.text_input(
                "Name", value=enemy["name"], key=f"enemy_name_{i}"
            )

            c1, c2, c3, c_sp, c4, c5, c6 = st.columns(
                [1.2, 2.4, 1.2, 0.6, 1.2, 2.4, 1.2]
            )

            with c1:
                st.button(
                    "➖",
                    key=f"e_h_dec_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_enemy_health(idx, -1),
                )
            with c2:
                st.markdown(f"**Health:** {enemy['health']} / {MAX_HEALTH}")
            with c3:
                st.button(
                    "➕",
                    key=f"e_h_inc_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_enemy_health(idx, 1),
                )

            with c4:
                st.button(
                    "➖",
                    key=f"e_m_dec_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_enemy_mana(idx, -1),
                )
            with c5:
                st.markdown(f"**Mana:** {enemy['mana']} / {MAX_MANA}")
            with c6:
                st.button(
                    "➕",
                    key=f"e_m_inc_{i}",
                    use_container_width=True,
                    on_click=lambda idx=i: update_enemy_mana(idx, 1),
                )

            if st.button("Remove", key=f"e_rm_{i}"):
                remove_enemy(i)
                st.rerun()

st.caption(f"Caps: Health = {MAX_HEALTH}, Mana = {MAX_MANA}")
