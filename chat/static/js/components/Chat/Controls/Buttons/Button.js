import React from "react";
import styles from './Button.css'
import {toast} from "react-toastify";

export default class Button extends React.Component {
    constructor(props) {
        super();
        this.props = props;
        this.state = {
            running: false,
        };
        this.triggerAction = this.triggerAction.bind(this);
        this.updateStatus = this.updateStatus.bind(this);
    }

    componentDidMount() {
        this.updateStatus();
    }

    updateStatus() {
        $.ajax({
            url: this.props.statusUrl,
            data: this.props.statusParams,
            method: 'GET',
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
            success: function (data) {
                let newStatus = data[this.props.statusKey];
                if (newStatus !== this.state.running) {
                    if (!newStatus) {
                        toast.success(this.props.actionName + ' successful!', {
                            autoClose: 3500,
                        });
                    }
                }
                this.setState({
                    running: data[this.props.statusKey]
                });
                this.interval = setTimeout(this.updateStatus, this.props.pollInterval);
            }.bind(this)
        });
    }

    triggerAction(event) {
        event.preventDefault();
        $.ajax({
            url: this.props.actionUrl,
            method: 'POST',
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
        });
        this.setState({
            running: true
        });
        toast.info('started ' + this.props.actionName + '...', {
            autoClose: 3500,
        });
    }

    render() {
        return (
            <span onClick={this.triggerAction} className={styles.container}
                  data-tip={"trigger " + this.props.actionName}>
                <img src={this.props.iconUrl}
                     className={[styles.icon, this.state.running ? this.props.runningStyle : this.props.normalStyle]}/>
            </span>
        )
    }
}