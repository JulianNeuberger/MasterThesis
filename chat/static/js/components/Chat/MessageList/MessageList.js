import React from 'react'
import ReactDOM from 'react-dom'
import styles from './MessageList.css'

export default class MessageList extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.state = {
            data: [],
            scrollLock: false
        };
        this.loadMessagesFromServer = this.loadMessagesFromServer.bind(this);
        this.handleScroll = this.handleScroll.bind(this)
    }

    loadMessagesFromServer() {
        let props = this.props;
        $.ajax({
            url: props.url,
            data: {
                chatId: this.props.chatId
            },
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({data: data});
            }.bind(this)
        })
    }

    componentDidMount() {
        this.loadMessagesFromServer();
        this.interval = setInterval(this.loadMessagesFromServer, this.props.pollInterval);
        this.scrollToEnd();
    }

    componentWillDismount() {
        clearTimeout(this.interval);
    }

    componentDidUpdate() {
        this.scrollToEnd();
    }

    handleScroll(event) {
        console.log('scrolling!')
    }

    scrollToEnd() {
        if (!this.state.scrollLock) {
            this.listEndMarker.scrollIntoView({behavior: 'smooth'});
        }
    }

    render() {
        let messages = this.state.data.map(function (message) {
            let className = styles.other;
            if (message.sent_by === window.django.user.url) {
                className = styles.own;
            }
            return (
                <li key={message.url} className={className}>
                    <span className={styles.message}>{message.value}</span>
                </li>
            )
        });
        return (
            <div className={styles.container} onScroll={this.handleScroll}>
                <ul className={styles.list} ref="messageList">
                    {messages}
                </ul>
                <div ref={ele => {this.listEndMarker = ele;}}/>
            </div>
        )
    }
}