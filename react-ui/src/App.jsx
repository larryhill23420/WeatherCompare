import { useState, useEffect } from 'react'
import './App.css'

const COMPARE_URL = "https://ocw3et6rrpypcwcoeaj7gqzliy0oksgx.lambda-url.us-west-2.on.aws/"
const ADD_ZIP_URL = "https://ibaykpce4noeovznl5taqqqn2a0zeyuv.lambda-url.us-west-2.on.aws/"
const LIST_ZIPS_URL = "https://o262tabg6eggjlckjnr6nmm4tu0bjsru.lambda-url.us-west-2.on.aws/"

function App() {
  const [zips, setZips] = useState([])
  const [zip1, setZip1] = useState('')
  const [zip2, setZip2] = useState('')
  const [days, setDays] = useState('1')
  const [summary, setSummary] = useState(null)
  const [data, setData] = useState([])
  const [sorting, setSorting] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [newZip, setNewZip] = useState('')
  const [addDays, setAddDays] = useState('7')
  const [addStatus, setAddStatus] = useState('')

  useEffect(() => { loadZips() }, [])

  function loadZips() {
    fetch(LIST_ZIPS_URL)
      .then(r => r.json())
      .then(list => {
        setZips(list)
        if (list.length && !zip1) setZip1(list[0].zip)
        if (list.length > 1 && !zip2) setZip2(list[1].zip)
      })
  }

  function openAddModal() {
    setNewZip('')
    setAddDays('7')
    setAddStatus('')
    setShowModal(true)
  }

  function submitAddZip() {
    if (!/^\d{5}$/.test(newZip)) {
      setAddStatus('Zip must be 5 digits')
      return
    }
    setAddStatus('Adding...')
    const prevZip2 = zip2
    fetch(`${ADD_ZIP_URL}?zip=${newZip}&days=${addDays}`)
      .then(r => r.json())
      .then(result => {
        if (result.success) {
          setAddStatus(`Added ${result.place_name}`)
          setTimeout(() => {
            loadZips()
            setZip1(newZip)
            if (prevZip2) setZip2(prevZip2)
            setShowModal(false)
          }, 800)
        } else {
          setAddStatus(result.error || 'Failed')
        }
      })
      .catch(() => setAddStatus('Request failed or timed out'))
  }

  function compare() {
    setSummary(null)
    setData([])
    fetch(`${COMPARE_URL}?zip1=${zip1}&zip2=${zip2}&days=${days}`)
      .then(r => r.json())
      .then(res => {
        setSummary(res.summary)
        // Flatten into one row per zip for the grid
        const flat = []
        ;(res.rows || []).forEach(r => {
          flat.push({
            localTime: r.LocalTime?.replace('T', ' ').slice(0, 16),
            zip: r.ZipCode1,
            place: r.PlaceName1,
            temp: r.Temp1,
            tempDiff: r.TempDiff,
            rain: r.Rain1,
            rainDiff: r.RainDiff,
            humid: r.Humid1,
            humidDiff: r.HumidDiff,
            cloud: r.Cloud1,
            cloudDiff: r.CloudDiff,
            isZip1: true,
          })
          flat.push({
            localTime: r.LocalTime?.replace('T', ' ').slice(0, 16),
            zip: r.ZipCode2,
            place: r.PlaceName2,
            temp: r.Temp2,
            tempDiff: -r.TempDiff,
            rain: r.Rain2,
            rainDiff: -r.RainDiff,
            humid: r.Humid2,
            humidDiff: -r.HumidDiff,
            cloud: r.Cloud2,
            cloudDiff: -r.CloudDiff,
            isZip1: false,
          })
        })
        setData(flat)
      })
  }

  const columns = [
    { accessorKey: 'localTime', header: 'Local Time' },
    { accessorKey: 'zip', header: 'Zip' },
    { accessorKey: 'place', header: 'Place Name' },
    { accessorKey: 'temp', header: 'Temp' },
    { accessorKey: 'tempDiff', header: 'Temp Diff', cell: info => info.getValue() > 0 ? `+${info.getValue()}` : info.getValue() },
    { accessorKey: 'rain', header: 'Rain' },
    { accessorKey: 'rainDiff', header: 'Rain Diff', cell: info => info.getValue() > 0 ? `+${info.getValue()}` : info.getValue() },
    { accessorKey: 'humid', header: 'Humid' },
    { accessorKey: 'humidDiff', header: 'Humid Diff', cell: info => info.getValue() > 0 ? `+${info.getValue()}` : info.getValue() },
    { accessorKey: 'cloud', header: 'Cloud' },
    { accessorKey: 'cloudDiff', header: 'Cloud Diff', cell: info => info.getValue() > 0 ? `+${info.getValue()}` : info.getValue() },
  ]



  return (
    <div className="app">
      <h1>Weather Compare</h1>

      <button onClick={openAddModal}>Add Zip Code</button>

      <div className="controls">
        <select value={zip1} onChange={e => setZip1(e.target.value)}>
          {zips.map(z => <option key={z.zip} value={z.zip}>{z.placeName} ({z.zip})</option>)}
        </select>
        <select value={zip2} onChange={e => setZip2(e.target.value)}>
          {zips.map(z => <option key={z.zip} value={z.zip}>{z.placeName} ({z.zip})</option>)}
        </select>
        <select value={days} onChange={e => setDays(e.target.value)}>
          {[1,2,3,4,5,6,7].map(d => <option key={d} value={d}>{d} day{d>1?'s':''}</option>)}
        </select>
        <button onClick={compare}>Compare Weather</button>
      </div>

      {summary && (
        <div className="summary">
          <h3>7-Day Summary</h3>
          <table>
            <thead>
              <tr><th></th><th>{summary.zip1.place}</th><th>{summary.zip2.place}</th></tr>
            </thead>
            <tbody>
              <tr><td>Avg Temp</td><td>{summary.zip1.avg_temp}</td><td>{summary.zip2.avg_temp}</td></tr>
              <tr><td>High</td><td>{summary.zip1.high_temp}</td><td>{summary.zip2.high_temp}</td></tr>
              <tr><td>Low</td><td>{summary.zip1.low_temp}</td><td>{summary.zip2.low_temp}</td></tr>
              <tr><td>Total Precip</td><td>{summary.zip1.total_precip}</td><td>{summary.zip2.total_precip}</td></tr>
              <tr><td>Avg Cloud</td><td>{summary.zip1.avg_cloud}</td><td>{summary.zip2.avg_cloud}</td></tr>
            </tbody>
          </table>
        </div>
      )}

            <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Local Time</th>
              <th>Zip</th>
              <th>Place Name</th>
              <th>Temp</th>
              <th>Temp Diff</th>
              <th>Rain</th>
              <th>Rain Diff</th>
              <th>Humid</th>
              <th>Humid Diff</th>
              <th>Cloud</th>
              <th>Cloud Diff</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className={row.isZip1 ? 'zip1' : 'zip2'}>
                <td>{row.localTime}</td>
                <td>{row.zip}</td>
                <td>{row.place}</td>
                <td>{row.temp ?? ''}</td>
                <td>{row.tempDiff > 0 ? `+${row.tempDiff}` : row.tempDiff}</td>
                <td>{row.rain ?? ''}</td>
                <td>{row.rainDiff > 0 ? `+${row.rainDiff}` : row.rainDiff}</td>
                <td>{row.humid ?? ''}</td>
                <td>{row.humidDiff > 0 ? `+${row.humidDiff}` : row.humidDiff}</td>
                <td>{row.cloud ?? ''}</td>
                <td>{row.cloudDiff > 0 ? `+${row.cloudDiff}` : row.cloudDiff}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Add Zip Code</h3>
            <input value={newZip} onChange={e => setNewZip(e.target.value)} placeholder="5-digit zip" maxLength={5} />
            <select value={addDays} onChange={e => setAddDays(e.target.value)}>
              <option value="1">1 day</option>
              <option value="7">7 days</option>
            </select>
            <div>
              <button onClick={submitAddZip}>Add</button>
              <button onClick={() => setShowModal(false)}>Cancel</button>
            </div>
            <div>{addStatus}</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App