import React from 'react'
import styles from './MessageInput.module.css'

export default class MessageInput extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: ''};
        this.handleInputChange = this.handleInputChange.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
    }

    handleInputChange(event) {
        this.setState({value: event.target.value})
    }

    sendMessage(event) {
        event.preventDefault();
        this.props.onSend(this.state.value);
        this.setState({value: ''});
    }

    render() {
        return (
            <div className={styles.container}>
                <form onSubmit={this.sendMessage}>
                    <input type={"text"}
                           placeholder={"Start typing..."}
                           className={styles.input}
                           value={this.state.value}
                           onChange={this.handleInputChange}/>
                    <button className={styles.send}>
                    </button>
                </form>
            </div>
        )
    }
}