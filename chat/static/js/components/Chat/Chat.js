import React from 'react'
import MessageList from './MessageList/MessageList'
import MessageInput from './MessageInput/MessageInput'
import styles from './Chat.css'

export default class Chat extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.state = {data: []};
    }

    render() {
        if (this.state.data) {
            return (
                <div className={styles.container}>
                    <MessageList url={this.props.url}
                                 chatId={this.props.chatId}
                                 csrfToken={this.props.csrfToken}
                                 scrollLockTrigger={5}
                                 pollInterval={1000}/>
                    <MessageInput url={this.props.url}
                                  csrfToken={this.props.csrfToken}
                                  userId={this.props.userId}
                                  chatId={this.props.chatId}/>
                </div>
            )
        }
    }
}