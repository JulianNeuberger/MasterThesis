import React from 'react'
import styles from './MessageList.module.css'
import Message from "./Message/Message";

export default class MessageList extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.state = {
            data: [],
            scrollLock: false
        };
        this.shouldScroll = true;
        this.loadNewMessagesFromServer = this.loadNewMessagesFromServer.bind(this);
    }

    loadNewMessagesFromServer() {
        let lastMessage = this.state.data.length > 0 ? this.state.data[this.state.data.length - 1] : undefined;
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
                    let newData = this.state.data.concat(data);
                    let messageCount = newData.length;
                    newData = messageCount > 150 ? newData.slice(messageCount - 150, messageCount) : newData;
                    this.setState({
                        data: newData
                    })
                }
                this.interval = setTimeout(this.loadNewMessagesFromServer, this.props.pollInterval);
            }.bind(this)
        })
    }


    messagesChanged(newList) {
        const oldList = this.state.data;
        let changed = oldList.length !== newList.length;
        if (changed) {
            return true;
        } else {
            if (oldList.length === 0) {
                return false;
            } else {
                return oldList[oldList.length - 1].id !== newList[newList.length - 1].id;
            }
        }
    }

    shouldComponentUpdate(nextProps, nextState) {
        return this.messagesChanged(nextState.data)
    }


    componentWillUpdate(nextProps, nextState) {
        const scrollPosition = this.messageList.scrollTop;
        const scrolledDown = this.messageList.scrollHeight - this.messageList.clientHeight;
        const stateChanged = this.state.data.length !== nextState.data.length;
        this.shouldScroll = scrollPosition <= 0 || scrollPosition === scrolledDown;
    }

    componentDidUpdate(prevProps, prevState) {
        this.listEndMarker.scrollIntoView({block: 'end', behavior: 'smooth'})
    }

    componentDidMount() {
        this.loadNewMessagesFromServer();
    }

    componentWillDismount() {
        clearTimeout(this.interval);
    }

    scrollToEnd() {
        if (this.shouldScroll) {
            this.listEndMarker.scrollIntoView({behavior: 'smooth'});
        }
    }

    render() {
        let messages = this.state.data.map(function (message) {
            return (
                <Message url={this.props.url}
                         key={message.id}
                         id={message.id}
                         value={message.value}
                         reward={message.reward}
                         sent_by={message.sent_by}
                         csrfToken={this.props.csrfToken}/>
            )
        }.bind(this));
        return (
            <div className={styles.container} ref={ele => {
                this.messageList = ele
            }}>
                <ul className={styles.list} ref="messageList">
                    {messages}
                </ul>
                <div className={styles.listEnd} ref={ele => {
                    this.listEndMarker = ele;
                }}/>
            </div>
        )
    }
}