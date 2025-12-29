import { useState, useEffect } from 'react'
import axios from 'axios'
import { Plus, Trash2, Play, Clock, Hash, User, TestTube } from 'lucide-react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

function App() {
  const [jobs, setJobs] = useState([])
  const [showAddJob, setShowAddJob] = useState(false)
  const [newJob, setNewJob] = useState({
    x_username: '',
    frequency: 'daily',
    topics: '',
    email: ''
  })
  const [summaries, setSummaries] = useState({})
  const [loading, setLoading] = useState(false)
  const [showTest, setShowTest] = useState(false)
  const [testData, setTestData] = useState({
    x_username: '',
    hours_back: 24,
    topics: '',
    email: ''
  })
  const [testResult, setTestResult] = useState(null)
  const [testLoading, setTestLoading] = useState(false)

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/jobs/`)
      setJobs(response.data)
    } catch (error) {
      console.error('Error loading jobs:', error)
    }
  }

  const addJob = async () => {
    if (!newJob.x_username.trim()) {
      alert('Please enter an X username')
      return
    }
    
    try {
      const topics = newJob.topics.split(',').map(t => t.trim()).filter(t => t)
      const response = await axios.post(`${API_BASE}/jobs/`, {
        x_username: newJob.x_username.trim(),
        frequency: newJob.frequency,
        topics: topics,
        email: newJob.email.trim() || null
      })
      setJobs([...jobs, response.data])
      setNewJob({ x_username: '', frequency: 'daily', topics: '', email: '' })
      setShowAddJob(false)
    } catch (error) {
      alert('Error creating job: ' + (error.response?.data?.detail || error.message))
    }
  }

  const deleteJob = async (jobId) => {
    try {
      await axios.delete(`${API_BASE}/jobs/${jobId}`)
      setJobs(jobs.filter(j => j.id !== jobId))
    } catch (error) {
      alert('Error deleting job: ' + (error.response?.data?.detail || error.message))
    }
  }

  const toggleJob = async (job) => {
    try {
      const response = await axios.patch(`${API_BASE}/jobs/${job.id}`, {
        is_active: !job.is_active
      })
      setJobs(jobs.map(j => j.id === job.id ? response.data : j))
    } catch (error) {
      alert('Error updating job: ' + (error.response?.data?.detail || error.message))
    }
  }

  const runJob = async (jobId) => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/monitoring/jobs/${jobId}/run`)
      // Reload summaries to show the new one
      await loadSummaries(jobId)
      alert('Job completed! Summary generated successfully.')
    } catch (error) {
      alert('Error running job: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const loadSummaries = async (jobId) => {
    try {
      const response = await axios.get(`${API_BASE}/jobs/${jobId}/summaries`)
      setSummaries({ ...summaries, [jobId]: response.data })
    } catch (error) {
      console.error('Error loading summaries:', error)
    }
  }

  const sendSummaryEmail = async (jobId, summaryId, email) => {
    if (!email || !email.trim()) {
      const userEmail = prompt('Please enter your email address:')
      if (!userEmail) return
      email = userEmail
    }
    
    setLoading(true)
    try {
      const response = await axios.post(
        `${API_BASE}/monitoring/jobs/${jobId}/summaries/send-email`,
        {
          email: email.trim(),
          summary_id: summaryId
        }
      )
      
      if (response.data.email_sent) {
        alert(`✅ Email sent successfully to ${email}!`)
      } else {
        alert('⚠️ Email service not configured. Please set up Gmail API credentials.')
      }
    } catch (error) {
      alert('Error sending email: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const runTest = async () => {
    if (!testData.x_username.trim()) {
      alert('Please enter an X username')
      return
    }
    
    setTestLoading(true)
    setTestResult(null)
    try {
      const topics = testData.topics.split(',').map(t => t.trim()).filter(t => t)
      const response = await axios.post(`${API_BASE}/monitoring/test`, {
        x_username: testData.x_username.trim(),
        hours_back: parseInt(testData.hours_back) || 24,
        topics: topics,
        email: testData.email.trim() || null
      })
      setTestResult(response.data)
    } catch (error) {
      let errorMessage = error.response?.data?.detail || error.message
      if (error.response?.status === 429) {
        errorMessage = 'Rate limit exceeded. The Twitter API allows 1 request every 5 seconds. Please wait a moment and try again.'
      }
      alert('Error running test: ' + errorMessage)
    } finally {
      setTestLoading(false)
    }
  }

  const frequencyOptions = [
    { value: 'hourly', label: 'Hourly' },
    { value: 'every_6_hours', label: 'Every 6 Hours' },
    { value: 'every_12_hours', label: 'Every 12 Hours' },
    { value: 'daily', label: 'Daily' }
  ]

  return (
    <div className="app">
      <div className="header">
        <h1>XTrack</h1>
        <p>Monitor X accounts and get AI summaries</p>
      </div>

      {/* Test Section */}
      <div className="test-container">
        <div className="jobs-header">
          <h2>Quick Test</h2>
          <button className="btn-primary" onClick={() => setShowTest(!showTest)}>
            <TestTube size={20} />
            {showTest ? 'Hide Test' : 'Show Test'}
          </button>
        </div>

        {showTest && (
          <div className="card test-card">
            <h3>Test Monitoring (Execute Immediately)</h3>
            <p className="test-description">Test the monitoring functionality with a specific time range without creating a job.</p>
            <div className="rate-limit-notice">
              <strong>Note:</strong> The Twitter API free tier allows 1 request every 5 seconds. Requests will automatically wait to respect this limit.
            </div>
            
            <div className="form-group">
              <label>
                <User size={16} />
                X Username (without @)
              </label>
              <input
                type="text"
                placeholder="elonmusk"
                value={testData.x_username}
                onChange={(e) => setTestData({ ...testData, x_username: e.target.value })}
              />
            </div>
            
            <div className="form-group">
              <label>
                <Clock size={16} />
                Hours Back (time range)
              </label>
              <input
                type="number"
                placeholder="24"
                min="1"
                max="168"
                value={testData.hours_back}
                onChange={(e) => setTestData({ ...testData, hours_back: e.target.value })}
              />
              <small>How many hours back to search (1-168 hours / 1 week)</small>
            </div>
            
            <div className="form-group">
              <label>
                <Hash size={16} />
                Topics (comma-separated, optional)
              </label>
              <input
                type="text"
                placeholder="AI, technology, space"
                value={testData.topics}
                onChange={(e) => setTestData({ ...testData, topics: e.target.value })}
              />
            </div>
            
            <div className="form-group">
              <label>
                📧 Email (optional - to receive summary)
              </label>
              <input
                type="email"
                placeholder="your@email.com"
                value={testData.email}
                onChange={(e) => setTestData({ ...testData, email: e.target.value })}
              />
              <small>If provided, the summary will be sent to this email address</small>
            </div>
            
            <div className="form-actions">
              <button 
                className="btn-primary" 
                onClick={runTest}
                disabled={testLoading}
              >
                {testLoading ? 'Running Test...' : 'Run Test'}
              </button>
            </div>

            {testResult && (
              <div className="test-result">
                <h4>Test Results</h4>
                <div className="test-meta">
                  <span><strong>Username:</strong> @{testResult.x_username}</span>
                  <span><strong>Tweets Found:</strong> {testResult.tweets_found}</span>
                  <span><strong>Time Range:</strong> Last {testResult.hours_back} hours</span>
                  {testResult.topics && testResult.topics.length > 0 && (
                    <span><strong>Topics:</strong> {testResult.topics.join(', ')}</span>
                  )}
                </div>
                
                <div className="summary-card">
                  <div className="summary-header">
                    <span className="summary-date">AI Summary</span>
                  </div>
                  <div className="summary-content">
                    {testResult.summary}
                  </div>
                  <div className="summary-stats">
                    Analyzed {testResult.tweets_found} tweet{testResult.tweets_found !== 1 ? 's' : ''}
                  </div>
                </div>

                {testResult.tweets && testResult.tweets.length > 0 && (
                  <div className="tweets-preview">
                    <h5>Sample Tweets ({testResult.tweets.length} shown):</h5>
                    {testResult.tweets.map((tweet, idx) => (
                      <div key={idx} className="tweet-preview">
                        <div className="tweet-text">{tweet.text}</div>
                        <div className="tweet-meta">
                          <span>❤️ {tweet.likes || 0}</span>
                          <span>🔄 {tweet.reposts || 0}</span>
                          <span>{new Date(tweet.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="jobs-container">
        <div className="jobs-header">
          <h2>Monitoring Jobs</h2>
          <button className="btn-primary" onClick={() => setShowAddJob(!showAddJob)}>
            <Plus size={20} />
            Add Job
          </button>
        </div>

        {showAddJob && (
          <div className="card add-job-card">
            <h3>Add New Monitoring Job</h3>
            <div className="form-group">
              <label>
                <User size={16} />
                X Username (without @)
              </label>
              <input
                type="text"
                placeholder="elonmusk"
                value={newJob.x_username}
                onChange={(e) => setNewJob({ ...newJob, x_username: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>
                <Clock size={16} />
                Frequency
              </label>
              <select
                value={newJob.frequency}
                onChange={(e) => setNewJob({ ...newJob, frequency: e.target.value })}
              >
                {frequencyOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>
                <Hash size={16} />
                Topics (comma-separated)
              </label>
              <input
                type="text"
                placeholder="AI, technology, space"
                value={newJob.topics}
                onChange={(e) => setNewJob({ ...newJob, topics: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>
                📧 Email (optional - to receive summaries)
              </label>
              <input
                type="email"
                placeholder="your@email.com"
                value={newJob.email}
                onChange={(e) => setNewJob({ ...newJob, email: e.target.value })}
              />
              <small>If provided, summaries will be automatically sent to this email when the job runs</small>
            </div>
            <div className="form-actions">
              <button className="btn-secondary" onClick={() => setShowAddJob(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={addJob}>
                Create Job
              </button>
            </div>
          </div>
        )}

        {jobs.length === 0 ? (
          <div className="card empty-state">
            <p>No monitoring jobs yet. Create one to get started!</p>
          </div>
        ) : (
          jobs.map(job => (
            <div key={job.id} className="card job-card">
              <div className="job-header">
                <div className="job-info">
                  <h3>@{job.x_username}</h3>
                  <div className="job-meta">
                    <span className="badge">
                      <Clock size={14} />
                      {frequencyOptions.find(o => o.value === job.frequency)?.label}
                    </span>
                    {job.topics && job.topics.length > 0 && (
                      <span className="badge">
                        <Hash size={14} />
                        {job.topics.length} topic{job.topics.length > 1 ? 's' : ''}
                      </span>
                    )}
                    <span className={`status ${job.is_active ? 'active' : 'inactive'}`}>
                      {job.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                <div className="job-actions">
                  <button
                    className="btn-icon"
                    onClick={() => runJob(job.id)}
                    title="Run now"
                    disabled={loading}
                  >
                    <Play size={18} />
                  </button>
                  <button
                    className="btn-icon"
                    onClick={() => toggleJob(job)}
                    title={job.is_active ? 'Pause' : 'Resume'}
                  >
                    {job.is_active ? '⏸' : '▶'}
                  </button>
                  <button
                    className="btn-icon danger"
                    onClick={() => deleteJob(job.id)}
                    title="Delete"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              {job.topics && job.topics.length > 0 && (
                <div className="topics">
                  <strong>Topics:</strong> {job.topics.join(', ')}
                </div>
              )}

              <div className="summaries-section">
                <button
                  className="btn-link"
                  onClick={() => loadSummaries(job.id)}
                >
                  View Summaries ({Array.isArray(summaries[job.id]) ? summaries[job.id].length : (summaries[job.id] ? 1 : 0)})
                </button>
                    {summaries[job.id] && (
                      <div className="summaries">
                        {(Array.isArray(summaries[job.id]) ? summaries[job.id] : [summaries[job.id]])
                          .filter(s => s)
                          .map((summary, idx) => (
                            <div key={summary.id || idx} className="summary-card">
                              <div className="summary-header">
                                <span className="summary-date">
                                  {new Date(summary.created_at).toLocaleString()}
                                </span>
                                <button
                                  className="btn-icon"
                                  onClick={() => sendSummaryEmail(job.id, summary.id, job.email)}
                                  title="Send via email"
                                  disabled={loading}
                                >
                                  📧
                                </button>
                              </div>
                              <div className="summary-content">
                                {summary.content}
                              </div>
                              {summary.raw_data?.count && (
                                <div className="summary-stats">
                                  Analyzed {summary.raw_data.count} tweet{summary.raw_data.count !== 1 ? 's' : ''}
                                </div>
                              )}
                            </div>
                          ))}
                      </div>
                    )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default App

