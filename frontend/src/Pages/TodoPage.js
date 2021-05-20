import React,{useState, useEffect} from 'react';
import { Card } from '../Components/Card';

export const TodoPage = ()=> {

    const [todo, setTodo] = useState([])
    
    useEffect(()=> {
        console.log("fetching")
        fetch('/api').then(response => {
            if(response.ok) {
                return response.json()
            }
        }).then(data => console.log(data))

    }, [])

    return (
        <>
            <Card/>
        </>
    )
}