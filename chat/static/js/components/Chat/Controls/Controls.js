import React from "react";
import styles from './Controls.module.css'
import Button from "./Buttons/Button";
import InformationModal from "./InformationModal/InformationModal";

export default class Controls extends React.Component {
    constructor(props) {
        super();
        this.props = props;
        this.state = {
            helpOpen: true
        };
        this.triggerHelpModal = this.triggerHelpModal.bind(this);
        this.triggerTraining = this.triggerTraining.bind(this);
        this.triggerSave = this.triggerSave.bind(this);
    }

    triggerTraining() {

    }

    triggerSave() {

    }

    triggerHelpModal() {
        this.setState({
            helpOpen: true
        });
        console.log('called handler')
    }

    render() {
        return (
            <span>
                <div className={styles.container}>
                    <Button style='normal' hovering={true}
                            iconSrc={'/static/img/brain-gear.svg'}
                            onClick={this.triggerTraining}>
                        train
                    </Button>
                    <Button style='normal' hovering={true}
                            iconSrc={'/static/img/floppy-solid.svg'}
                            onClick={this.triggerSave}>
                        save
                    </Button>
                    <Button style='normal' hovering={true}
                            iconSrc={'/static/img/question.svg'}
                            onClick={this.triggerHelpModal}>
                        help
                    </Button>
                </div>
                <InformationModal open={this.state.helpOpen}/>
            </span>
        );
    }
}