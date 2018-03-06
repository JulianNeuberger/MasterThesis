import React from 'react'
import styles from './Message.css'
import MessageRating from "./MessageRating/MessageRating";

export default class Message extends React.Component {
    constructor(props) {
        super(props);
        this.VIDEO_REGEX = /youtube.com\/(?:embed\/|watch\?v=)([a-zA-Z0-9_-]{11})/;
        this.IMAGE_REGEX = /([^\s]*\.(?:jpg|jpeg|png|gif))/;

    }

    render() {
        let className = styles.other;
        let isUserMessage = parseInt(this.props.sent_by) === parseInt(window.django.user.id);
        if (isUserMessage) {
            className = styles.own;
        }
        let ratingComponent = isUserMessage ? (null) : (<MessageRating name={'interaction quality'}
                                                                       csrfToken={this.props.csrfToken}
                                                                       current={parseFloat(this.props.reward)}
                                                                       url={this.props.url + this.props.id + "/"}/>);
        return (
            <li key={this.props.id} className={className}>
                <span className={styles.message}>
                    <div>
                        {this.props.value}
                        {this.renderRichContent()}
                    </div>
                    {ratingComponent}
                </span>
            </li>
        )
    }

    renderUrls() {

    }

    renderRichContent() {
        let match = this.VIDEO_REGEX.exec(this.props.value);
        if (match) {
            const url = 'https://www.youtube.com/embed/' + match[1];
            return (
                <div className={styles["rich-container"]}>
                    <iframe src={url}/>
                </div>
            );
        }
        match = this.IMAGE_REGEX.exec(this.props.value);
        if (match) {
            const url= match[1];
            return (
                <div className={styles["rich-container"]}>
                    <img src={url}/>
                </div>
            )
        }
        return (null);
    }

    renderVideo() {

    }
}