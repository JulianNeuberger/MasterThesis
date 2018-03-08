import React from 'react'
import ReactTooltip from 'react-tooltip'
import {ToastContainer} from "react-toastify"

import styles from './Chat.module.css'
import MessageList from './MessageList/MessageList'
import MessageInput from './MessageInput/MessageInput'
import Controls from "./Controls/Controls";

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
                    <Controls trainActionUrl={this.props.trainActionUrl}
                              trainStatusUrl={this.props.trainStatusUrl}
                              saveActionurl={this.props.saveActionUrl}
                              saveStatusUrl={this.props.saveStatusUrl}
                              csrfToken={this.props.csrfToken}
                              pollInterval={3000}/>
                    <ToastContainer/>
                    <ReactTooltip effect='solid' type='light'/>
                </div>
            )
        }
    }
}