import streamlit as st
import requests

# Specify your backend URL
BACKEND_URL = "http://127.0.0.1:8000"

def clear_token():
    """Clears the authentication token from the session state."""
    if 'auth_token' in st.session_state:
        del st.session_state['auth_token']
    st.experimental_set_query_params(auth_token=None)

def check_for_token():
    """Checks for the presence of an authentication token in the query parameters."""
    query_params = st.experimental_get_query_params()
    if 'auth_token' in query_params:
        return query_params['auth_token'][0]
    return None

def save_token(token):
    """Saves the authentication token into the session state and query parameters."""
    st.session_state['auth_token'] = token
    st.experimental_set_query_params(auth_token=token)

def show_home_page():
    """Displays the home page of the To-Do application."""
    st.title("To-Do App")
    st.info("Welcome! Use the buttons below to navigate between Login and SignUp.")

def show_login_page():
    """Displays the login form in the center of the application."""
    st.subheader("Login Section")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type='password', key="login_password")
    
    if st.button("Login"):
        response = requests.post(f"{BACKEND_URL}/token", data={"username": username, "password": password})
        if response.status_code == 200:
            st.success(f"Logged In as {username}")
            token = response.json().get("access_token")
            save_token(token)
            st.experimental_rerun()
        else:
            st.error("Incorrect Username/Password")

def show_signup_page():
    """Displays the signup form in the center of the application."""
    st.subheader("Create New Account")
    new_user = st.text_input("New Username", key="signup_new_user")
    new_password = st.text_input("New Password", type='password', key="signup_new_password")
    
    if st.button("Create Account"):
        response = requests.post(f"{BACKEND_URL}/users/", json={"username": new_user, "password": new_password})
        if response.status_code == 200:
            st.success("You have successfully created a new account! Please log in.")
        else:
            st.error("Username already taken")

def show_todo_page(token):
    """Displays the To-Do page for authenticated users to manage their tasks."""
    st.title("Your To-Do List")
    headers = {"Authorization": f"Bearer {token}"}
    
    with st.form(key='todo_form'):
        title = st.text_input("Title", placeholder="Enter a title for your to-do")
        description = st.text_area("Description", placeholder="Describe your to-do")
        submit_button = st.form_submit_button(label='Add To-Do')
        
    if submit_button and title and description:
        todo_data = {"title": title, "description": description}
        response = requests.post(f"{BACKEND_URL}/todos/", json=todo_data, headers=headers)
        if response.status_code in [200, 201]:
            st.success("To-Do added successfully!")
            st.experimental_rerun()
        else:
            st.error("Failed to add To-Do.")
    
    display_todos(token, headers)
def display_todos(token, headers):
    """Fetches and displays the user's To-Do items with an option to delete each."""
    todos_response = requests.get(f"{BACKEND_URL}/todos/", headers=headers)
    if todos_response.status_code == 200:
        todos = todos_response.json()
        if todos:
            for todo in todos:
                with st.expander(f"{todo['title']}"):
                    st.write(f"Description: {todo['description']}")
                    st.write(f"Completed: {'Yes' if todo['completed'] else 'No'}")
                    
                    # Delete button for each to-do
                    delete_button = st.button("Delete", key=f"delete_{todo['id']}")
                    if delete_button:
                        delete_response = requests.delete(f"{BACKEND_URL}/todos/{todo['id']}", headers=headers)
                        if delete_response.status_code in [200, 204]:
                            st.success("To-Do deleted successfully.")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to delete To-Do.")
        else:
            st.write("You have no To-Dos yet. Start by adding a new one!")


                # Implement functionality for marking as complete or deleting here if applicable

def main():
    """Controls the main flow of the application."""
    st.set_page_config(page_title='To-Do App', layout='centered')
    
    token = check_for_token()

    if not token:
        show_home_page()
        app_mode = st.radio("Choose an option", ["Login", "SignUp"])
        
        if app_mode == "Login":
            show_login_page()
        elif app_mode == "SignUp":
            show_signup_page()
    else:
        show_todo_page(token)
        
        if st.button("Logout"):
            clear_token()
            st.experimental_rerun()

if __name__ == '__main__':
    main()
