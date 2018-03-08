import React from 'react'
import ReactDOM from 'react-dom'
import Chat from './components/Chat/Chat'

ReactDOM.render(<Chat url='/chat/api/messages/'
                      settingsUrl='/chat/settings/tutorial'
                      trainActionUrl='/bot/train/'
                      trainStatusUrl='/bot/status/'
                      saveActionUrl='/bot/save/'
                      saveStatusUrl='/bot/status/'
                      chatId={window.django.chat.id}
                      user={window.django.user}
                      csrfToken={window.django.csrfToken}
                      settings={window.django.user.settings}
                      pollInterval={1000}/>, document.getElementById('container'));