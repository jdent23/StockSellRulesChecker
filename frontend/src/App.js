import logo from './logo.svg';
import './App.css';
import { Header } from './Components/Header'
import { Container } from './Components/Container'
import { MarketDirection } from './Components/MarketDirection'

function App() {
  return (
    <div className="App">
      <div className="Title">
        <h1 className="TitleText">Stock Sell Rules Checker</h1>
      </div>
      <MarketDirection/>
      <Container/>
    </div>

  );
}

export default App;
