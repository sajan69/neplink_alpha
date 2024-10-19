
# NepLink API Documentation

## Table of Contents

1. [Authentication](#authentication)
2. [Accounts](#accounts)
3. [Friends](#friends)
4. [Posts](#posts)
5. [Chat](#chat)

## Authentication

All API endpoints, except for registration and login, require authentication. Use the token received upon login in the Authorization header:

```
Authorization: Token <your_token_here>
```

## Accounts

### Register a new user

- **URL**: `/accounts-api/register/`
- **Method**: POST
- **Auth required**: No
- **Permissions**: AllowAny

**Request Body**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "password2": "string",
  "first_name": "string",
  "last_name": "string"
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**:
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string"
  },
  "token": "string"
}
```

### Login

- **URL**: `/accounts-api/login/`
- **Method**: POST
- **Auth required**: No
- **Permissions**: AllowAny

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "token": "string"
}
```

### Get User Profile

- **URL**: `/accounts-api/users/{id}/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "profile_pic": "url_to_image",
  "cover_photo": "url_to_image",
  "is_private": boolean,
  "show_email": boolean,
  "show_full_name": boolean
}
```

### Update User Profile

- **URL**: `/accounts-api/users/{id}/`
- **Method**: PUT/PATCH
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "bio": "string",
  "profile_pic": "file",
  "cover_photo": "file",
  "is_private": boolean,
  "show_email": boolean,
  "show_full_name": boolean
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**: Updated user object

### List Notifications

- **URL**: `/accounts-api/notifications/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `search`: Search notifications by title or body
- `ordering`: Order results by timestamp
- `read`: Filter by read status (true/false)

**Success Response**:
- **Code**: 200 OK
- **Content**: List of notification objects

### Mark Notification as Read

- **URL**: `/accounts-api/notifications/{id}/mark_as_read/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "status": "notification marked as read"
}
```

### Mark All Notifications as Read

- **URL**: `/accounts-api/notifications/mark_all_as_read/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "status": "all notifications marked as read"
}
```

## Friends

### List Friends

- **URL**: `/friends-api/friends/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `search`: Search friends by username or email
- `ordering`: Order results by created_at

**Success Response**:
- **Code**: 200 OK
- **Content**: List of friendship objects

### Send Friend Request

- **URL**: `/friends-api/friends/send_friend_request/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "to_user_id": 1
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**:
```json
{
  "message": "Friend request sent"
}
```

### Accept Friend Request

- **URL**: `/friends-api/friends/accept_friend_request/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "request_id": 1
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "message": "Friend request accepted"
}
```

### Reject Friend Request

- **URL**: `/friends-api/friends/reject_friend_request/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "request_id": 1
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "message": "Friend request rejected"
}
```

### Remove Friend

- **URL**: `/friends-api/friends/remove_friend/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "friend_id": 1
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "message": "Friend removed"
}
```

### List Friend Requests

- **URL**: `/friends-api/friend-requests/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `ordering`: Order results by created_at

**Success Response**:
- **Code**: 200 OK
- **Content**: List of friend request objects

## Posts

### List Posts

- **URL**: `/posts-api/posts/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `search`: Search posts by caption or username
- `ordering`: Order results by created_at or updated_at
- `visibility`: Filter by visibility
- `is_hidden`: Filter by hidden status
- `is_shared`: Filter by shared status

**Success Response**:
- **Code**: 200 OK
- **Content**: List of post objects

### Create Post

- **URL**: `/posts-api/posts/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "caption": "string",
  "visibility": "string",
  "feeling": "string",
  "tagged_users": [1, 2, 3],
  "files": [file1, file2]
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created post object

### Get Post Detail

- **URL**: `/posts-api/posts/{id}/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 200 OK
- **Content**: Post object

### Update Post

- **URL**: `/posts-api/posts/{id}/`
- **Method**: PUT/PATCH
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "caption": "string",
  "visibility": "string",
  "feeling": "string",
  "is_hidden": boolean
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**: Updated post object

### Delete Post

- **URL**: `/posts-api/posts/{id}/`
- **Method**: DELETE
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 204 No Content

### Like/Unlike Post

- **URL**: `/posts-api/posts/{id}/like/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "message": "Post liked" // or "Post unliked"
}
```

### Add Comment to Post

- **URL**: `/posts-api/posts/{id}/add_comment/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "text": "string"
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created comment object

### Share Post

- **URL**: `/posts-api/posts/{id}/share/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "caption": "string"
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created shared post object

### List Comments

- **URL**: `/posts-api/comments/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `ordering`: Order results by created_at

**Success Response**:
- **Code**: 200 OK
- **Content**: List of comment objects

### Like/Unlike Comment

- **URL**: `/posts-api/comments/{id}/like/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "message": "Comment liked" // or "Comment unliked"
}
```

### Add Reply to Comment

- **URL**: `/posts-api/comments/{id}/add_reply/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "text": "string"
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created reply object

## Chat

### List Chat Rooms

- **URL**: `/chat-api/chat-rooms/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `search`: Search chat rooms by name
- `ordering`: Order results by created_at
- `is_group_chat`: Filter by group chat status

**Success Response**:
- **Code**: 200 OK
- **Content**: List of chat room objects

### Create or Open Private Chat

- **URL**: `/chat-api/chat-rooms/create_or_open_private_chat/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "friend_id": 1
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created or existing chat room object

### Create Group Chat

- **URL**: `/chat-api/chat-rooms/create_group_chat/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "name": "string",
  "participant_ids": [1, 2, 3]
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created group chat room object

### List Messages

- **URL**: `/chat-api/messages/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `ordering`: Order results by timestamp

**Success Response**:
- **Code**: 200 OK
- **Content**: List of message objects

### Send Message

- **URL**: `/chat-api/messages/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "room": 1,
  "content": "string",
  "is_file": boolean,
  "file": file
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created message object

### List Call Logs

- **URL**: `/chat-api/call-logs/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `ordering`: Order results by start_time
- `status`: Filter by call status
- `call_type`: Filter by call type

**Success Response**:
- **Code**: 200 OK
- **Content**: List of call log objects

### Initiate Call

- **URL**: `/chat-api/call-logs/initiate_call/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Request Body**:
```json
{
  "room_id": 1,
  "call_type": "string"
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**: Created call log object

### End Call

- **URL**: `/chat-api/call-logs/{id}/end_call/`
- **Method**: POST
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Success Response**:
- **Code**: 200 OK
- **Content**: Updated call log object

### Get Agora Token

- **URL**: `/chat-api/call-logs/get_agora_token/`
- **Method**: GET
- **Auth required**: Yes
- **Permissions**: IsAuthenticated

**Query Parameters**:
- `channel`: Agora channel name

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "token": "string",
  "uid": 1,
  "app_id": "string"
}
