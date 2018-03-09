import React from "react";
import Modal from "react-modal"
import styles from "./InformationModal.module.css"
import Button from "../Buttons/Button";

export default class InformationModal extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
    }

    render() {
        const visibilityClass = this.props.open ? styles.open : '';
        return (
            <Modal isOpen={this.props.open}
                   className={[styles.container, visibilityClass].join(' ')}
                   overlayClassName={[styles.overlay, visibilityClass].join(' ')}
                   shouldCloseOnEsc={true}
                   shouldCloseOnOverlayClick={true}
                   closeTimeoutMS={500}
                   ariaHideApp={false}
                   onRequestClose={this.props.onClose}>
                <div className={styles.content}>
                    <img src={'/static/img/bot.png'} className={styles.icon}/>
                    <h3> Welcome to [BOTNAME]!</h3>
                    <p>
                        This Bot can <b>answer questions</b> (age, height, number of goals), <b>show you videos</b> and
                        <b>pictures</b> for these soccer players: Müller, Lewandowski, Messi, Suarez, Neymar, Mbappé,
                        Ronaldo, Ibrahimović, Pogba, Dybala and Higuaín.
                    </p>
                    <p>
                        This information is displayed, since [BOTNAME] employs a reinforcement learning technique to
                        learn how to answer your questions. This includes the question: <i>"What can you do?"</i>, which
                        means, it may not have learned how to answer this question.
                    </p>
                    <p>
                        You can train [BOTNAME] by talking to it and rating its responses at the little&nbsp;
                        <img src={"/static/img/star-full.svg"} style={{height: '1em'}}/>
                        &nbsp;button!
                    </p>
                    <p>
                        Here is a more detailed overview of what you can do:
                        <ul>
                            <li>ask for a list of known players</li>
                            <li>ask for videos/pictures of a player</li>
                            <li>ask for information (age, height, #goals) of a certain player</li>
                            <li>small talk like "hi", "how are you", "bye"...</li>
                        </ul>
                    </p>
                    <p>
                        How about starting with a <i>"Hello"</i> to [BOTNAME]?
                    </p>
                    <p>
                        <Button onClick={this.props.onClose} style={"light"} size={"medium"} hovering={true}>
                            Got it!
                        </Button>
                        <Button onClick={this.props.onDisable} style={"subtle"} size={"medium"} hovering={false}>
                            Don't show again
                        </Button>
                    </p>
                </div>
            </Modal>
        )
    }
}