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
        this.updateBotStatus = this.updateBotStatus.bind(this);
    }

    componentDidMount() {
        this.updateBotStatus();
        this.interval = setInterval(this.updateBotStatus, this.props.pollInterval);
    }

    updateBotStatus() {
        $.ajax({
            url: this.props.statusUrl,
            success: function (data) {
                console.log(data['training']);
                this.setState({
                    training: data['training']
                })
            }.bind(this)
        });
    }

    triggerTraining(event) {
        event.preventDefault();
        $.ajax({
            url: this.props.trainingUrl
        });
        this.setState({
            training: true
        });
    }

    render() {
        return (
            <a href={this.props.trainingUrl} onClick={this.triggerTraining} className={styles.container}>
                <span>
                    <img src={'/static/img/dumbbell.svg'}
                         className={this.state.training ? styles.training : styles.normal}/>
                    <span>train</span>
                </span>
            </a>
        )
    }
}