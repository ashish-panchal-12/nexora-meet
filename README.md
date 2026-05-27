# Nexora Meet 🚀

Nexora Meet is a modern real-time video conferencing web application inspired by Zoom and Google Meet. It enables users to create, join, and manage virtual meetings with live video communication, authentication, and real-time chat features.

## 🌐 Live Demo
Coming Soon

## ✨ Features

- User Registration & Login Authentication
- Create meetings with unique Meeting IDs
- Join meetings using Meeting IDs
- Real-time video conferencing
- Live meeting chat using WebSockets
- Meeting dashboard
- Schedule meetings
- Meeting history
- Responsive modern UI
- Profile management
- Copy invite links
- Leave / End meetings

---

## 🛠 Tech Stack

### Backend
- Python
- Django
- Django REST Framework

### Real-Time Features
- Django Channels
- WebSockets
- Redis

### Video Conferencing
- Jitsi Meet API / JaaS

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Database
- SQLite (Development)
- PostgreSQL (Production)

### Deployment
- Render
- GitHub

---

## 📁 Project Structure

```text
zoom_project/
│
├── accounts/
├── meetings/
├── chat/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
├── zoom_project/
├── manage.py
├── requirements.txt

└── README.md

└── README.md



roomName:
        "vpaas-magic-cookie-65eeae3b11f64ed5bf97ee3c2a548de7/Nexora_{{meeting.meeting_id}}",