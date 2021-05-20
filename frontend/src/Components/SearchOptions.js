import React, { Component } from 'react';

export function ApplyFilter(columns, data_row, filter_options) {

    let passes_filter = true;
    Object.getOwnPropertyNames(filter_options).map(function(key) {
        let index = columns.indexOf(key);

        if(filter_options[key].data_type === "string") {
            passes_filter = passes_filter & data_row[index].toUpperCase().includes(filter_options[key].value.toUpperCase());
        } else if(filter_options[key].data_type === "boolean") {
            if(filter_options[key].value != null) {
                passes_filter = passes_filter & (data_row[index] === filter_options[key].value);
            }
        } else if(filter_options[key].data_type === "number") {
            if(isNaN(filter_options[key].gt) === false) {
                passes_filter = passes_filter & (data_row[index] > filter_options[key].gt);
            }

            if(isNaN(filter_options[key].lt) === false) {
                passes_filter = passes_filter & (data_row[index] < filter_options[key].lt);
            }
        }
    })

    return passes_filter;
}

function build_form_element(element_name, data_type, on_string_change, on_number_change) {
    if(data_type === "number") {

        let greater_than_name = element_name + "_gt";
        let less_than_name = element_name + "_lt";

        return <div className="FormElement"><text>{element_name.split('_').join(' ')} is strictly greater than </text>
                <input type="number" name={greater_than_name} onChange={on_number_change}/>
                <text> and less than </text>
                <input type="number" name={less_than_name} onChange={on_number_change}/></div>

    } else if (data_type === "boolean") {
        return <div className="FormElement"><text>{element_name.split('_').join(' ')} is </text>
                    <select name={element_name} onChange={on_string_change}>
                        <option value="any">any</option>
                        <option value="true">true</option>
                        <option value="false">false</option>
                    </select>
                </div>
    }
    return <div className="FormElement"><text>{element_name.split('_').join(' ')} contains </text>
            <input type="text" name={element_name} onChange={on_string_change}/></div>
}


export class SearchOptions extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    
        this.handleStringChange = this.handleStringChange.bind(this);
        this.handleNumberChange = this.handleNumberChange.bind(this);
      }
    
      handleStringChange(event) {
        const target = event.target;
        const name = target.name;
        var local_state = this.state;

        if(target.value === "true") {
            local_state[name] = { "value" : true, "data_type" : "boolean"};
        } else if(target.value === "false") {
            local_state[name] = { "value" : false, "data_type" : "boolean"};
        } else if(target.value === "any") {
            local_state[name] = { "value" : null, "data_type" : "boolean"};
        } else {
            local_state[name] = { "value" : target.value, "data_type" : "string"};
        }
        
        this.setState(local_state);
        this.props.set_search_options(local_state);
      }

      handleNumberChange(event) {
        const target = event.target;
        const name = target.name;
        var local_state = this.state;
        let filter_name = name.slice(0, name.length-3)

        if(( filter_name in local_state) === false) {
            local_state[filter_name] = {"gt": NaN, "lt": NaN, "data_type" : "number"}
        }
        local_state[filter_name][name.slice(name.length-2, name.length)] = parseFloat(target.value);
        this.setState(local_state);
        this.props.set_search_options(local_state);
      }

        handleSubmit(event){
            event.preventDefault();
            event.target.reset();
            this.setState({});
            this.props.set_search_options({});
        }

    render() {

        return <div>
                    <h2 style={{textAlign: "right"}}>Table Ticker Filter Form</h2>
                    <form onSubmit={this.handleSubmit.bind(this)}>
                        <div class="FormElement"><input type="submit" value="Clear Form" ></input></div>
                        {this.props.option_names.map((option, i) => build_form_element(option, this.props.data_types[i], this.handleStringChange, this.handleNumberChange))}
                    </form>
                </div>
    }
}