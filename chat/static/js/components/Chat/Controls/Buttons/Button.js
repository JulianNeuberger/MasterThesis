import React from "react";
import styles from './Button.module.css'

export default class Button extends React.Component {
    constructor(props) {
        super();
        this.props = props;
        this.state = {
            running: false,
        };
        this.sizeMap = {
            'small': styles.small,
            'medium': styles.medium,
            'big': styles.big
        };
        this.styleMap = {
            'light': styles.light,
            'normal': styles.normal,
            'secondary': styles.secondary,
            'subtle': styles.subtle
        }
    }

    render() {
        let style = this.getFromMap(this.styleMap, this.props.style, 'normal');
        let hovering = this.props.hovering ? styles.hovering : '';
        let size = this.getFromMap(this.sizeMap, this.props.size, 'medium');
        return (
            <span onClick={this.props.onClick}
                  className={[styles.container, style, hovering, size].join(' ')}
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

    getFromMap(map, key, defaultValue) {
        let value = map[key];
        if (typeof(value) === 'undefined') {
            value = defaultValue;
        }
        return value;
    }
}