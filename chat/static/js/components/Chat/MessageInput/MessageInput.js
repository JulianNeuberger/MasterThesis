import React from 'react'
import styles from './MessageInput.module.css'

export default class MessageInput extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: ''};
        this.handleInputChange = this.handleInputChange.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
    }

    componentDidMount() {
    }

    componentWillDismount() {
    }

    handleInputChange(event) {
        this.setState({value: event.target.value})
    }

    sendMessage(event) {
        event.preventDefault();

        $.post({
            url: this.props.url,
            datatype: 'json',
            headers: {
                'X-CSRFToken': this.props.csrfToken
            },
            data: {
                value: this.state.value,
                sent_by: this.props.userId,
                sent_in: this.props.chatId
            }
        });

        this.setState({value: ''});
    }

    render() {
        return (
            <div className={styles.container}>
                <form onSubmit={this.sendMessage}>
                    <input type="text"
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