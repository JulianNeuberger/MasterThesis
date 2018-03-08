import React from "react";
import styles from './Button.module.css'

export default class Button extends React.Component {
    constructor(props) {
        super();
        this.props = props;
        this.state = {
            running: false,
        };
        this.styleMap = {
            'light': styles.light,
            'normal': styles.normal
        }
    }

    render() {
        let buttonStyle = this.styleMap[this.props.style];
        if (typeof(buttonStyle) === 'undefined') {
            buttonStyle = this.styleMap.normal;
        }
        let hoveringStyle = this.props.hovering ? styles.hovering : '';
        return (
            <span onClick={this.props.onClick}
                  className={[styles.container, buttonStyle, hoveringStyle].join(' ')}
                  data-tip={"trigger " + this.props.actionName}>
                {this.renderIcon()}
                {this.renderText()}
            </span>
        )
    }

    renderIcon() {
        if (typeof(this.props.iconSrc) !== 'undefined') {
            return (<img src={this.props.iconSrc} className={styles.icon}/>)
        } else {
            return (null)
        }
    }

    renderText() {
        if (typeof(this.props.children) !== 'undefined' && this.props.children.length > 0) {
            return (<span className={styles.text}>{this.props.children}</span>)
        } else {
            return (null)
        }
    }
}