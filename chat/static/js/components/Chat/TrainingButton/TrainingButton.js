import React from 'react'
import styles from './TrainingButton.css'

export default class TrainingButton extends React.Component {
    constructor(props) {
        super();
        this.props = props;
        this.state = {
            training: false
        };
        this.triggerTraining = this.triggerTraining.bind(this);
    }

    triggerTraining(event) {
        event.preventDefault();
        $.ajax({
            url: this.props.url,
            success: function(data) {
                this.setState({
                    training: true
                })
            }.bind(this)
        })
    }

    render() {
        return (
            <div className={styles.container}>
                <a href={this.props.url} onClick={this.triggerTraining}>train</a>
            </div>
        )
    }
}