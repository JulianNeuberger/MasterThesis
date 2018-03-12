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
        this.state = {messages: [], helpOpen: this.props.user.settings.show_tutorial};

        this.onWillSendMessage = this.onWillSendMessage.bind(this);
        this.loadNewMessagesFromServer = this.loadNewMessagesFromServer.bind(this);
        this.updateState = this.updateState.bind(this);
        this.openHelp = this.openHelp.bind(this);
        this.closeHelp = this.closeHelp.bind(this);
        this.onMessageRating = this.onMessageRating.bind(this);
        this.disableHelp = this.disableHelp.bind(this);

        this.pollInterval = 1000;
    }

    updateState() {
        this.loadNewMessagesFromServer();
    }

    componentWillUnmount() {
        clearInterval(this.updateInterval);
    }

    componentDidMount() {
        this.updateState();
        this.openHelp();
        this.updateInterval = setInterval(this.updateState, this.pollInterval);
    }

    loadNewMessagesFromServer() {
        let lastMessage = this.state.messages.length > 0 ? this.state.messages[this.state.messages.length - 1] : undefined;
        $.ajax({
            url: this.props.url,
            method: 'GET',
            data: {
                'sent_in_id': this.props.chatId,
                'sent_on__gt': typeof(lastMessage) !== 'undefined' ? lastMessage.sent_on : undefined
            },
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
            datatype: 'json',
            cache: false,
            success: function (data) {
                if (typeof(data) !== 'undefined' && data.length > 0) {
                    let newData = this.state.messages.concat(data);
                    let messageCount = newData.length;
                    newData = messageCount > 25 ? newData.slice(messageCount - 25, messageCount) : newData;
                    this.setState({
                        messages: newData
                    })
                }
            }.bind(this)
        })
    }

    onWillSendMessage(message) {
        $.post({
            url: this.props.url,
            datatype: 'json',
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
            data: {
                value: message,
                sent_by: this.props.user.id,
                sent_in: this.props.chatId
            }
        });
    }

    openHelp() {
        this.setState({
            helpOpen: true
        });
    }

    closeHelp() {
        this.setState({
            helpOpen: false
        });
    }

    disableHelp() {
        this.closeHelp();
        $.ajax({
            url: this.props.settingsUrl,
            method: 'POST',
            datatype: 'json',
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
            data: JSON.stringify({
                show: false,
            }),
            cache: false,
        });
    }

    onMessageRating(id, rating) {
        const url = this.props.url + id + "/";
        $.ajax({
            url: url,
            data: {
                reward: rating
            },
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
            method: 'PATCH',
            datatype: 'json',
            cache: false
        });
    }

    render() {
        if (this.state.messages) {
            return (
                <div className={styles.container}>
                    <MessageList messages={this.state.messages} onMessageRating={this.onMessageRating}/>
                    <MessageInput onSend={this.onWillSendMessage}/>
                    <Controls triggerTraining={this.triggerTraining}
                              triggerSave={this.triggerSave}
                              triggerHelp={this.openHelp}
                              helpOpen={this.state.helpOpen}
                              onHelpClose={this.closeHelp}
                              onHelpDisable={this.disableHelp}/>
                    <ToastContainer/>
                    <ReactTooltip effect='solid' type='light'/>
                </div>
            )
        }
    }
}