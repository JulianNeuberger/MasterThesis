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
                    <img src={'/static/img/question.svg'} className={styles.icon}/>
                    <h3> Welcome !</h3>
                    <p>
                        This chat bot is a proof of concept for my master's thesis. It is designed to answer your
                        questions regarding your favourite football <i>(soccer)</i> players. For example it can tell
                        you how old Thomas Müller is, or show you a video of Ronaldo, Mbappe and others.
                    </p>
                    <p>
                        This bot employs a <b>machine learning</b> technique called reinforcment learning,
                        which allows it to learn when to do which action <i>(e.g. what it should say)</i>!
                    </p>
                    <p>
                        To do this, it needs your help! BOTNAME HERE can only learn through experience, so
                        it will test random responses to your questions. Rate these answers to improve the bot!
                    </p>
                    <p>
                        Depending on when you chose to visit, it may feel very dumb and random, but don't be afraid,
                        it will constantly learn and improve. Just talk a little to it and rate its responses!
                    </p>
                    <p>
                        Thank you for your help in training BOTNAME HERE!
                    </p>
                    <p>
                        <Button onClick={this.props.onClose} style={"light"} hovering={true}>Got it!</Button>
                        <Button onClick={this.props.onDisable} style={"subtle"} hovering={false}>
                            Don't show again
                        </Button>
                    </p>
                </div>
            </Modal>
        )
    }
}