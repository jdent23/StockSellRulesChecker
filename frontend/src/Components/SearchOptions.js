import React, { Component } from 'react';

function build_form_element(element_name, data_type, on_change) {
    if(data_type === "number") {
        return <div className="FormElement"><text>{element_name.split('_').join(' ')} is greater than </text>
                <input type="number" name={element_name}_gt onChange={on_change}/>
                <text> and less than </text>
                <input type="number" name={element_name}_lt onChange={on_change}/></div>

    } else if (data_type === "boolean") {
        return <div className="FormElement"><text>{element_name.split('_').join(' ')} is </text>
                    <select name={element_name} onChange={on_change}>
                        <option value="any">any</option>
                        <option value="true">true</option>
                        <option value="false">false</option>
                    </select>
                </div>
    }
    return <div className="FormElement"><text>{element_name.split('_').join(' ')} contains </text>
            <input type="text" name={element_name} onChange={on_change}/></div>
}


export class SearchOptions extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    
        this.handleInputChange = this.handleInputChange.bind(this);
      }
    
      handleInputChange(event) {
        const target = event.target;
        const name = target.name;
        var local_state = this.state;
        local_state[name] = target.value;
        this.setState(local_state);
        console.log("Child state options")
        console.log(this.state);
        this.props.set_search_options(local_state);
      }
    render() {

        return <div>
                    <form>
                        {this.props.option_names.map((option, i) => build_form_element(option, this.props.data_types[i], this.handleInputChange))}
                    </form>
                </div>
    }
}