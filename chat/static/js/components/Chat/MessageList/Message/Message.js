import React from 'react'
import styles from './Message.module.css'
import MessageRating from "./MessageRating/MessageRating";
import Button from "../../Controls/Buttons/Button";

export default class Message extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
        this.state = {};

        this.VIDEO_REGEX = /youtube.com\/(?:embed\/|watch\?v=)([a-zA-Z0-9_-]{11})/;
        this.IMAGE_REGEX = /([^\s]*\.(?:jpg|jpeg|png|gif))/;
    }

    openOverlay(overlay) {
        this.setState({
            openOverlay: this.state.openOverlay === overlay ? undefined : overlay
        })
    }

    render() {
        let className = styles.other;
        let isUserMessage = parseInt(this.props.message.sent_by) === parseInt(window.django.user.id);
        if (isUserMessage) {
            className = styles.own;
        }
        let ratingComponent = isUserMessage ? (null) : (<MessageRating for={this.props.message}
                                                                       name={'interaction quality'}
                                                                       onRate={this.props.onRate}/>);

        let messageControls = isUserMessage ? (null) : (
            <div className={styles.controls}>
                <Button iconSrc={'/static/img/question.svg'}
                        style={'secondary'} size={'small'}
                        onClick={function () {
                            this.openOverlay(this.informationText)
                        }.bind(this)}/>
                <Button iconSrc={'/static/img/star-full.svg'}
                        style={'secondary'} size={'small'}
                        onClick={function () {
                            this.openOverlay(this.ratingComponent)
                        }.bind(this)}/>
            </div>
        );
        let overlays = isUserMessage ? (null) : (
            <div className={styles.overlay}>
                <div ref={ele => this.informationText = ele}
                     data-open={this.state.openOverlay === this.informationText ? "true" : "false"}>
                    rate the way, the bot responded to your message
                </div>
                <div ref={ele => this.ratingComponent = ele}
                     data-open={this.state.openOverlay === this.ratingComponent ? "true" : "false"}>
                    {ratingComponent}
                </div>
            </div>
        );
        return (
            <li key={this.props.message.id} className={className}>
                <span className={styles.message}
                      data-overlay-open={typeof(this.state.openOverlay) !== 'undefined' ? "true" : "false"}>
                    {overlays}
                    {messageControls}
                    <div>
                        {this.props.message.value}
                        {this.renderRichContent()}
                    </div>
                </span>
                <img className={styles["user-icon"]}
                     src={isUserMessage ? '/static/img/user.svg' : '/static/img/bot.svg'}/>
            </li>
        )
    }

    renderRichContent() {
        let match = this.VIDEO_REGEX.exec(this.props.message.value);
        if (match) {
            const url = 'https://www.youtube.com/embed/' + match[1];
            return (
                <div className={[styles["rich-container"], styles["video-container"]].join(' ')}>
                    <iframe src={url}/>
                </div>
            );
        }
        match = this.IMAGE_REGEX.exec(this.props.message.value);
        if (match) {
            const url = match[1];
            return (
                <div className={styles["rich-container"]}>
                    <img src={url}/>
                </div>
            )
        }
        return (null);
    }
}