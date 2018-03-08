import React from 'react'
import styles from './MessageList.module.css'
import Message from "./Message/Message";

export default class MessageList extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
    }

    messagesChanged(newList) {
        const oldList = this.props.messages;
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
        return this.messagesChanged(nextProps.messages)
    }

    componentDidUpdate(prevProps, prevState) {
        this.listEndMarker.scrollIntoView({block: 'end', behavior: 'smooth'})
    }

    render() {
        let messages = this.props.messages.map(function (message) {
            return (
                <Message key={message.id} message={message} onRate={this.props.onMessageRating}/>
            )
        }.bind(this));
        return (
            <div className={styles.container}>
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