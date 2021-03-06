import React from "react";
import styles from './Controls.module.css'
import Button from "./Buttons/Button";
import InformationModal from "./InformationModal/InformationModal";

export default class Controls extends React.Component {
    constructor(props) {
        super();
        this.props = props;
    }

    render() {
        return (
            <span>
                <div className={styles.container}>
                    <Button style='normal' hovering={true} size={'medium'}
                            iconSrc={'/static/img/question.svg'}
                            onClick={this.props.triggerHelp}>
                        help
                    </Button>
                </div>
                <InformationModal open={this.props.helpOpen}
                                  onClose={this.props.onHelpClose}
                                  onDisable={this.props.onHelpDisable}/>
            </span>
        );
    }
}