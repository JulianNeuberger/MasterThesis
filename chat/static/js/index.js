import React from 'react'
import ReactDOM from 'react-dom'
import Chat from './components/Chat/Chat'

ReactDOM.render(<Chat url='/chat/api/messages/'
                      trainActionUrl='/bot/train/'
                      trainStatusUrl='/bot/status/'
                      saveActionUrl='/bot/save/'
                      saveStatusUrl='/bot/status/'
                      chatId={window.django.chat.id}
                      userId={window.django.user.id}
                      csrfToken={window.django.csrfToken}
                      pollInterval={1000}/>, document.getElementById('container'));