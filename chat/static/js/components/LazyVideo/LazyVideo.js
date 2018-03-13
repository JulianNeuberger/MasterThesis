// https://img.youtube.com/vi/g6iDZspbRMg/1.jpg

import React from "react";
import styles from './LazyVideo.module.css'

export default class LazyVideo extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false
        }
    }

    loadVideo(event) {
        this.setState({
            loaded: true
        })
    }

    render() {
        return (
            <div className={styles.container}>
                {this.renderContent()}
            </div>
        )
    }

    renderContent() {
        if (this.state.loaded) {
            const url = 'https://www.youtube.com/embed/' + this.props.videoId + '?autoplay=1';
            return (
                <iframe src={url} className={styles.video}/>
            );
        } else {
            const url = 'https://img.youtube.com/vi/' + this.props.videoId + '/0.jpg';
            return (
                <div onClick={(e) => this.loadVideo(e)} src={url} className={styles.preview} style={{
                    backgroundImage: 'url("' + url + '")'
                }}/>
            );
        }
    }
}