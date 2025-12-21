import streamlit as st


def display_notifications(connection, cursor, user_id):
    st.sidebar.subheader("Notifications")

    cursor.execute(
        "SELECT id, message, is_read FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    notifications = cursor.fetchall()

    unread_count = sum(1 for n in notifications if not n[2])

    if unread_count > 0:
        st.sidebar.markdown(
            f"**You have {unread_count} unread notifications!** 🔔")
    else:
        st.sidebar.markdown("No new notifications. 🔕")

    with st.sidebar.expander("View All Notifications"):
        if not notifications:
            st.write("No notifications yet.")
        else:
            for notification in notifications:
                notif_id, message, is_read = notification
                if not is_read:
                    st.markdown(f"**{message}**")
                else:
                    st.write(message)

            if unread_count > 0:
                if st.button("Mark all as read"):
                    try:
                        cursor.execute(
                            "UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))
                        connection.commit()
                        st.rerun()
                    except Exception as e:
                        st.error("Could not mark notifications as read.")
