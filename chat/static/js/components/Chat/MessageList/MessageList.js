import React from 'react'
import styles from './MessageList.css'
import MessageRating from "./MessageRating/MessageRating";

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
        if ($(window).scrollTop() + $(window).height() == $(document).height()) {
            this.scrollToEnd();
        }
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
            let isUserMessage = message.sent_by === window.django.user.url;
            if (isUserMessage) {
                className = styles.own;
            }
            let ratingComponent = isUserMessage ? (null) : (<MessageRating name={'Interaction'}
                                                                           csrfToken={this.props.csrfToken}
                                                                           current={parseFloat(message.reward)}
                                                                           url={message.url}/>);
            return (
                <li key={message.url} className={className}>
                    <span className={styles.message}>
                        <div>{message.value}</div>
                        {ratingComponent}
                    </span>
                </li>
            )
        }.bind(this));
        return (
            <div className={styles.container} onScroll={this.handleScroll}>
                <ul className={styles.list} ref="messageList">
                    {messages}
                </ul>
                <div ref={ele => {
                    this.listEndMarker = ele;
                }}/>
            </div>
        )
    }
}