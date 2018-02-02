import React from 'react'
import ReactDOM from 'react-dom'
import Chat from './components/Chat/Chat'
// import '!style-loader!css-loader!font-awesome/css/font-awesome.min.css';

ReactDOM.render(<Chat url='/chat/api/messages/'
                      chatId={window.django.chat.url}
                      userId={window.django.user.url}
                      csrfToken={window.django.csrfToken}
                      pollInterval={1000}/>, document.getElementById('container'));