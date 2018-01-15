import React from 'react'
import ReactDOM from 'react-dom'
import Chat from './components/Chat/Chat'

console.log(window.django.csrfToken);
ReactDOM.render(<Chat url='/chat/api/messages/'
                      chatId={window.django.chat.url}
                      userId={window.django.user.url}
                      csrfToken={window.django.csrfToken}
                      pollInterval={1000}/>, document.getElementById('container'));