# Import required libraries for Rasa
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
import openai  # Added this import for OpenAI integration
import requests  # For making HTTP requests
import datetime  # Importing the datetime module

# Setting up the OpenAI API key
openai.api_key = "sk-9eEQnvYOaXszpfbuBRX3BlbkFJRGyu5nI6AIPbTpfYF1qA"  # Make sure to replace with your actual API key

# Base URL for API requests
BASE_URL = "https://backend.projects-ai.de/api"

# Function to get auth headers (assuming you have a way to retrieve the user's token)
def get_auth_headers(tracker: Tracker) -> Dict[str, str]:
    token = tracker.get_slot('%22eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2OTk3MjgyMTgsImlhdCI6MTY5OTY0MTgxMywic3ViIjoiVmlzaGVzaCJ9.cuaS-mz_2hXnXlPO86YgLSs83sZpOVfERKr8ltwoUX0%22')
    return {'Authorization': f'Bearer {token}'}

# Function to handle API requests
def make_api_request(method: str, url: str, headers: Dict[str, str], data: Dict = None, params: Dict = None):
    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, params=params)
    else:
        return "Invalid HTTP method specified"

    if response.ok:
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"

class ActionOpenAIResponse(Action):
    def name(self) -> str:
        return "action_openai_response"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        
        # Fetching response from OpenAI instead of the hardcoded response
        openai_response = self.get_openai_response(user_message)

        dispatcher.utter_message(text=openai_response)
        return []

    @staticmethod
    def get_openai_response(user_message: str) -> str:
        """Helper method to get response from OpenAI."""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content'].strip()

class ActionProjectsAIRequest(Action):
    def name(self) -> str:
        return "action_projects_ai_request"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        api_url = "https://backend.projects-ai.de/api/checklist/getListsOfUser"
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2OTk3MjgyMTgsImlhdCI6MTY5OTY0MTgxMywic3ViIjoiVmlzaGVzaCJ9.cuaS-mz_2hXnXlPO86YgLSs83sZpOVfERKr8ltwoUX0"  # Use a secure method to handle tokens
        username = "Vishesh"  # Replace with dynamic username if required

        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{api_url}?token=%22{token}%22&username={username}', headers=headers)

        if response.ok:
            data = response.json()
            # Assuming data is a list of dicts
            if data and isinstance(data, list):
                html_table = self._create_html_table(data)
                dispatcher.utter_message(html_table)
            else:
                dispatcher.utter_message(text="No data available.")
        else:
            dispatcher.utter_message(text="There was a problem processing your request.")

        return []

    def _create_html_table(self, data: List[Dict]) -> str:
        table_html = "<table>"
        # Add table headers
        table_html += "<tr>"
        for key in data[0].keys():
            table_html += f"<th>{key}</th>"
        table_html += "</tr>"
        # Add table rows
        for item in data:
            table_html += "<tr>"
            for value in item.values():
                table_html += f"<td>{value}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        return table_html

# Example actions for different API interactions
class ActionAddChecklist(Action):
    def name(self) -> Text:
        return "action_add_checklist"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        checklist_data = tracker.get_slot('checklist_data')  # Assuming you collect this data from the user
        url = f"{BASE_URL}/checklist"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=checklist_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to update an existing checklist
class ActionUpdateChecklist(Action):
    def name(self) -> Text:
        return "action_update_checklist"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        checklist_update_data = tracker.get_slot('checklist_update_data')
        url = f"{BASE_URL}/checklist"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('PUT', url, headers, data=checklist_update_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to delete multiple checklists
class ActionDeleteMultipleChecklists(Action):
    def name(self) -> Text:
        return "action_delete_multiple_checklists"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        checklist_ids = tracker.get_slot('checklist_ids')  # This should be a list of checklist IDs to delete
        url = f"{BASE_URL}/checklist"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'checklistIds': checklist_ids}
        response = make_api_request('DELETE', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to add a new sublist to an existing list
class ActionAddSublist(Action):
    def name(self) -> Text:
        return "action_add_sublist"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sublist_data = tracker.get_slot('sublist_data')
        url = f"{BASE_URL}/checklist/sublist"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=sublist_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to update an existing comment
class ActionUpdateComment(Action):
    def name(self) -> Text:
        return "action_update_comment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        comment_update_data = tracker.get_slot('comment_update_data')
        url = f"{BASE_URL}/checklist/comment"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('PUT', url, headers, data=comment_update_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to delete multiple sublists
class ActionDeleteMultipleSublists(Action):
    def name(self) -> Text:
        return "action_delete_multiple_sublists"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sublist_ids = tracker.get_slot('sublist_ids')  # A list of sublist IDs to delete
        url = f"{BASE_URL}/checklist/sublist"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'sublistIds': sublist_ids}
        response = make_api_request('DELETE', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to update sublist fields
class ActionUpdateSublistFields(Action):
    def name(self) -> Text:
        return "action_update_sublist_fields"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sublist_update_data = tracker.get_slot('sublist_update_data')
        url = f"{BASE_URL}/checklist/sublist/updateFields"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('PUT', url, headers, data=sublist_update_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to add a comment to a list-entry
class ActionAddComment(Action):
    def name(self) -> Text:
        return "action_add_comment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        comment_data = tracker.get_slot('comment_data')
        url = f"{BASE_URL}/checklist/comment"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=comment_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to delete multiple comments
class ActionDeleteMultipleComments(Action):
    def name(self) -> Text:
        return "action_delete_multiple_comments"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        comment_ids = tracker.get_slot('comment_ids')  # A list of comment IDs to delete
        url = f"{BASE_URL}/checklist/comment"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'commentIds': comment_ids}
        response = make_api_request('DELETE', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to get search results by typing
class ActionSearchResultByTyping(Action):
    def name(self) -> Text:
        return "action_search_result_by_typing"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        keyword = tracker.get_slot('search_keyword')
        url = f"{BASE_URL}/checklist/searchResultByTyping"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'keyword': keyword}
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to get search results by keyword
class ActionSearchResultByKeyword(Action):
    def name(self) -> Text:
        return "action_search_result_by_keyword"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        keyword = tracker.get_slot('search_keyword')
        url = f"{BASE_URL}/checklist/searchResultByKeyword"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'keyword': keyword}
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to get a single list by ID
class ActionGetSingleList(Action):
    def name(self) -> Text:
        return "action_get_single_list"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        list_id = tracker.get_slot('list_id')
        url = f"{BASE_URL}/checklist/singleList"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'listId': list_id}
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to find checklists by tags
class ActionFindChecklistsByTags(Action):
    def name(self) -> Text:
        return "action_find_checklists_by_tags"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tags = tracker.get_slot('tags')  # Should be a list of tags
        url = f"{BASE_URL}/checklist/findByTags"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'tags': tags}
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to modify list entry dependency
class ActionModifyListEntryDependency(Action):
    def name(self) -> Text:
        return "action_modify_list_entry_dependency"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dependency_data = tracker.get_slot('dependency_data')
        url = f"{BASE_URL}/listEntry/dependency"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=dependency_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to modify list entry tags
class ActionModifyListEntryTags(Action):
    def name(self) -> Text:
        return "action_modify_list_entry_tags"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tags_data = tracker.get_slot('tags_data')
        url = f"{BASE_URL}/listEntry/tags"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=tags_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to create a new user
class ActionCreateUser(Action):
    def name(self) -> Text:
        return "action_create_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_data = tracker.get_slot('user_data')
        url = f"{BASE_URL}/user/register"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=user_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to log a user into the system
class ActionLoginUser(Action):
    def name(self) -> Text:
        return "action_login_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username = tracker.get_slot('username')
        password = tracker.get_slot('password')
        url = f"{BASE_URL}/user/login"
        params = {'username': username, 'password': password}
        response = make_api_request('GET', url, headers={}, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to log out the current user
class ActionLogoutUser(Action):
    def name(self) -> Text:
        return "action_logout_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        url = f"{BASE_URL}/user/logout"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('GET', url, headers)
        dispatcher.utter_message(text=str(response))
        return []

# Action to get user data by token and username
class ActionGetUserByToken(Action):
    def name(self) -> Text:
        return "action_get_user_by_token"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_login_data = tracker.get_slot('user_login_data')
        url = f"{BASE_URL}/user/userData"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=user_login_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to update user details
class ActionUpdateUser(Action):
    def name(self) -> Text:
        return "action_update_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_update_data = tracker.get_slot('user_update_data')
        url = f"{BASE_URL}/user/userData"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('PUT', url, headers, data=user_update_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to delete a user
class ActionDeleteUser(Action):
    def name(self) -> Text:
        return "action_delete_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username = tracker.get_slot('username')
        url = f"{BASE_URL}/user/userData"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'username': username}
        response = make_api_request('DELETE', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to assign a list to a user
class ActionAssignListToUser(Action):
    def name(self) -> Text:
        return "action_assign_list_to_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        list_assignment_data = tracker.get_slot('list_assignment_data')
        url = f"{BASE_URL}/user/assignListToUser"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=list_assignment_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to assign a list entry to a user
class ActionAssignListEntryToUser(Action):
    def name(self) -> Text:
        return "action_assign_list_entry_to_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        list_entry_assignment_data = tracker.get_slot('list_entry_assignment_data')
        url = f"{BASE_URL}/user/assignListEntryToUser"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=list_entry_assignment_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to search users while typing
class ActionSearchUsersWhileTyping(Action):
    def name(self) -> Text:
        return "action_search_users_while_typing"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        keyword = tracker.get_slot('search_user_keyword')
        url = f"{BASE_URL}/user/searchUsersWhileTyping"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'keyword': keyword}
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to get users with schedule
class ActionGetUsersWithSchedule(Action):
    def name(self) -> Text:
        return "action_get_users_with_schedule"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        list_ids = tracker.get_slot('list_ids')
        scope = tracker.get_slot('scope')
        url = f"{BASE_URL}/user/usersWithSchedule"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'listIds': list_ids, 'scope': scope}
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to get users with skills
class ActionGetUsersWithSkills(Action):
    def name(self) -> Text:
        return "action_get_users_with_skills"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        list_ids = tracker.get_slot('list_ids')
        scope = tracker.get_slot('scope')
        url = f"{BASE_URL}/user/usersWithSkills"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = {'listIds': list_ids, 'scope': scope}
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to upload files to a list entry
class ActionUploadListEntryFiles(Action):
    def name(self) -> Text:
        return "action_upload_list_entry_files"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        file_details = tracker.get_slot('file_details')  # This should be handled appropriately as file upload
        url = f"{BASE_URL}/files/uploadListEntryFiles"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        # File upload requires a different request format, which might need to be handled specifically.
        response = make_api_request('POST', url, headers, data=file_details)
        dispatcher.utter_message(text=str(response))
        return []

# Action to read a file by filename
class ActionReadListEntryFileByFilename(Action):
    def name(self) -> Text:
        return "action_read_list_entry_file_by_filename"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        file_parameters = tracker.get_slot('file_parameters')
        url = f"{BASE_URL}/files/readListEntryFileByFilename"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        params = file_parameters  # This should include es_list_id, local_sublist_id, local_list_entry_id, filename
        response = make_api_request('GET', url, headers, params=params)
        dispatcher.utter_message(text=str(response))
        return []

# Action to upload new files to a list entry
class ActionUploadNewFilesToListEntry(Action):
    def name(self) -> Text:
        return "action_upload_new_files_to_list_entry"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        file_details = tracker.get_slot('file_details')  # Handle file details appropriately
        url = f"{BASE_URL}/files/uploadListEntryFiles"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        # Handle file upload request format
        response = make_api_request('POST', url, headers, data=file_details)
        dispatcher.utter_message(text=str(response))
        return []

# Action to read list entry file by filename
class ActionReadListEntryFile(Action):
    def name(self) -> Text:
        return "action_read_list_entry_file"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        file_read_parameters = tracker.get_slot('file_read_parameters')  # Includes es_list_id, local_sublist_id, etc.
        url = f"{BASE_URL}/files/readListEntryFileByFilename"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('GET', url, headers, params=file_read_parameters)
        dispatcher.utter_message(text=str(response))
        return []

# Action to modify dependency of a list entry
class ActionModifyDependencyOfListEntry(Action):
    def name(self) -> Text:
        return "action_modify_dependency_of_list_entry"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dependency_data = tracker.get_slot('dependency_data')
        url = f"{BASE_URL}/listEntry/dependency"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=dependency_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to modify tags of a list entry
class ActionModifyTagsOfListEntry(Action):
    def name(self) -> Text:
        return "action_modify_tags_of_list_entry"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tags_data = tracker.get_slot('tags_data')
        url = f"{BASE_URL}/listEntry/tags"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=tags_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to register a new user
class ActionRegisterNewUser(Action):
    def name(self) -> Text:
        return "action_register_new_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_data = tracker.get_slot('user_data')
        url = f"{BASE_URL}/user/register"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('POST', url, headers, data=user_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to log in a user
class ActionLogin(Action):
    def name(self) -> Text:
        return "action_login"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        login_data = {'username': tracker.get_slot('username'), 'password': tracker.get_slot('password')}
        url = f"{BASE_URL}/user/login"
        response = make_api_request('GET', url, headers={}, params=login_data)
        dispatcher.utter_message(text=str(response))
        return []

# Action to log out a user
class ActionLogout(Action):
    def name(self) -> Text:
        return "action_logout"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        url = f"{BASE_URL}/user/logout"
        headers = get_auth_headers(tracker)
        username = tracker.get_slot('Vishesh')
        response = make_api_request('GET', url, headers)
        dispatcher.utter_message(text=str(response))
        return []


class ActionGenericDispatcher(Action):
    def name(self) -> Text:
        return "action_generic_dispatcher"

    def handle_meeting_schedule(self, dispatcher, tracker):
        # Sample data - you should extract these from user messages or slots
        meeting_topic = "Scheduled Meeting"
        start_time = "2023-01-01T10:00:00"  # Format: "YYYY-MM-DDTHH:MM:SS" in UTC
        duration = 30  # Duration in minutes

        zoom_user_id = "your_zoom_user_id"  # Replace with your Zoom User ID
        api_key = "your_zoom_api_key"  # Replace with your Zoom JWT API Key
        api_secret = "your_zoom_api_secret"  # Replace with your Zoom JWT API Secret

        meeting_details = {
            "topic": meeting_topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time,
            "duration": duration,
            "timezone": "UTC",
            "agenda": "Meeting scheduled via chatbot",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "watermark": True,
                "use_pmi": False,
                "approval_type": 0,
                "registration_type": 1,
                "audio": "both",
                "auto_recording": "none",
                "enforce_login": False,
                "waiting_room": True,
            },
        }

        # Generate JWT token
        token = self.generate_jwt(api_key, api_secret)

        # Create Zoom meeting
        response = self.create_zoom_meeting(zoom_user_id, meeting_details, token)

        if response.status_code == 201:
            meeting_info = response.json()
            join_url = meeting_info["join_url"]
            dispatcher.utter_message(text=f"Meeting scheduled successfully. Join URL: {join_url}")
        else:
            dispatcher.utter_message(text=f"Failed to schedule meeting: {response.text}")

        return []

    @staticmethod
    def generate_jwt(api_key, api_secret):
        token_exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        payload = {
            "iss": api_key,
            "exp": token_exp
        }
        token = jwt.encode(payload, api_secret, algorithm='HS256')
        return token

    @staticmethod
    def create_zoom_meeting(zoom_user_id, meeting_details, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"https://api.zoom.us/v2/users/{zoom_user_id}/meetings", json=meeting_details, headers=headers)
        return response

