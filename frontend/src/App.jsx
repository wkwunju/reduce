import { useState, useEffect } from 'react'
import axios from 'axios'
import { Plus, Trash2, Zap, Clock, Hash, User, TestTube, Mail, Share2, Send } from 'lucide-react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import AuthFlow from './components/AuthFlow'
import Navbar from './components/Navbar'
import Profile from './components/Profile'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const PLAYGROUND_RUN_LIMIT = 10
const PLAYGROUND_WINDOW_MS = 24 * 60 * 60 * 1000
const PLAYGROUND_STORAGE_KEY = 'xtrack_playground_runs'
const MAX_TASKS_PER_USER = 5

function MainApp({ showAuthModal, setShowAuthModal, onShowProfile }) {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([])
  const [showAddJob, setShowAddJob] = useState(false)
  const [newJob, setNewJob] = useState({
    x_username: '',
    frequency: 'daily',
    topics: '',
    language: 'en',
    email: '',
    send_email: false,
    send_telegram: false,
    telegram_target_ids: []
  })
  const [summaries, setSummaries] = useState({})
  const [executions, setExecutions] = useState({})
  const [telegramTargets, setTelegramTargets] = useState([])
  const [loading, setLoading] = useState(false)
  const [testData, setTestData] = useState({
    x_username: '',
    hours_back: 24,
    topics: '',
    language: 'en'
  })
  const [testResult, setTestResult] = useState(null)
  const [testLoading, setTestLoading] = useState(false)
  const [activeView, setActiveView] = useState('playground') // 'playground' or 'tasks'
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [expandedExecutions, setExpandedExecutions] = useState({})

  const loadPlaygroundRuns = () => {
    if (typeof window === 'undefined') return []
    try {
      const raw = localStorage.getItem(PLAYGROUND_STORAGE_KEY)
      const parsed = raw ? JSON.parse(raw) : []
      if (!Array.isArray(parsed)) return []
      const cutoff = Date.now() - PLAYGROUND_WINDOW_MS
      return parsed.filter((timestamp) => typeof timestamp === 'number' && timestamp >= cutoff)
    } catch (error) {
      return []
    }
  }

  const getPlaygroundRemaining = () => {
    const recentRuns = loadPlaygroundRuns()
    return Math.max(0, PLAYGROUND_RUN_LIMIT - recentRuns.length)
  }

  const recordPlaygroundRun = () => {
    const recentRuns = loadPlaygroundRuns()
    const nextRuns = [...recentRuns, Date.now()]
    try {
      localStorage.setItem(PLAYGROUND_STORAGE_KEY, JSON.stringify(nextRuns))
    } catch (error) {
      // Ignore localStorage write failures.
    }
  }

  const normalizeSummary = (text = '') =>
    text
      .replace(/\*/g, '')
      .replace(/[ \t]{2,}/g, ' ')
      .replace(/\n{3,}/g, '\n\n')
      .trim()

  useEffect(() => {
    if (user) {
      loadJobs()
      loadTelegramTargets()
    } else {
      setActiveView('playground')
      setJobs([])
      setSummaries({})
      setExecutions({})
      setExpandedExecutions({})
      setTelegramTargets([])
    }
  }, [user])

  useEffect(() => {
    if (jobs.length > 0) {
      preloadExecutionCounts(jobs)
    }
  }, [jobs])

  useEffect(() => {
    if (jobs.length >= MAX_TASKS_PER_USER && showAddJob) {
      setShowAddJob(false)
    }
  }, [jobs, showAddJob])

  const loadJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/jobs/`)
      setJobs(response.data)
    } catch (error) {
      console.error('Error loading jobs:', error)
    }
  }

  const addJob = async () => {
    if (!user) {
      alert('Please login or register to create scheduled tasks')
      setShowAuthModal(true)
      return
    }

    if (jobs.length >= MAX_TASKS_PER_USER) {
      alert('You have reached the maximum of 5 scheduled tasks.')
      return
    }

    if (!newJob.x_username.trim()) {
      alert('Please enter an X username')
      return
    }
    
    const selectedTelegramTargetIds = newJob.send_telegram ? newJob.telegram_target_ids : []
    const hasTelegramTargets = telegramTargets.some((target) => target.channel === 'telegram')
    if (newJob.send_telegram && !hasTelegramTargets) {
      alert('Please bind a Telegram target first.')
      if (onShowProfile) {
        onShowProfile()
      }
      return
    }
    if (newJob.send_telegram && selectedTelegramTargetIds.length === 0) {
      alert('Please select at least one Telegram target.')
      return
    }

    try {
      const topics = newJob.topics.split(',').map(t => t.trim()).filter(t => t)
      const response = await axios.post(`${API_BASE}/jobs/`, {
        x_username: newJob.x_username.trim(),
        frequency: newJob.frequency,
        topics: topics,
        language: newJob.language,
        email: newJob.send_email ? user.email : null,
        notification_target_ids: selectedTelegramTargetIds.length > 0 ? selectedTelegramTargetIds : null
      })
      setJobs([...jobs, response.data])
      setNewJob({
        x_username: '',
        frequency: 'daily',
        topics: '',
        language: 'en',
        email: '',
        send_email: false,
        send_telegram: false,
        telegram_target_ids: []
      })
      setShowAddJob(false)
    } catch (error) {
      alert('Error creating task: ' + (error.response?.data?.detail || error.message))
    }
  }

  const deleteJob = async (jobId) => {
    try {
      await axios.delete(`${API_BASE}/jobs/${jobId}`)
      setJobs(jobs.filter(j => j.id !== jobId))
    } catch (error) {
      alert('Error deleting task: ' + (error.response?.data?.detail || error.message))
    }
  }

  const toggleJob = async (job) => {
    try {
      const response = await axios.patch(`${API_BASE}/jobs/${job.id}`, {
        is_active: !job.is_active
      })
      setJobs(jobs.map(j => j.id === job.id ? response.data : j))
    } catch (error) {
      alert('Error updating task: ' + (error.response?.data?.detail || error.message))
    }
  }

  const runJob = async (jobId) => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/monitoring/jobs/${jobId}/run`)
      await loadExecutions(jobId)
      alert('Task completed! Summary generated successfully.')
    } catch (error) {
      alert('Error running task: ' + (error.response?.data?.detail || error.message))
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

  const loadExecutions = async (jobId) => {
    try {
      const [executionsResponse, summariesResponse] = await Promise.all([
        axios.get(`${API_BASE}/jobs/${jobId}/executions`),
        axios.get(`${API_BASE}/jobs/${jobId}/summaries`)
      ])
      setExecutions((prev) => ({ ...prev, [jobId]: executionsResponse.data }))
      setSummaries((prev) => ({ ...prev, [jobId]: summariesResponse.data }))
    } catch (error) {
      console.error('Error loading executions:', error)
    }
  }

  const loadTelegramTargets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/notifications/targets`)
      setTelegramTargets(response.data || [])
    } catch (error) {
      console.error('Error loading Telegram targets:', error)
    }
  }

  const telegramTargetsForUser = telegramTargets.filter(
    (target) => target.channel === 'telegram'
  )

  const formatTelegramTargetLabel = (target) => {
    const label = target?.metadata?.title || target?.destination
    return label || 'Telegram target'
  }

  const preloadExecutionCounts = async (jobsList) => {
    try {
      const responses = await Promise.all(
        jobsList.map(job => Promise.all([
          axios.get(`${API_BASE}/jobs/${job.id}/executions`),
          axios.get(`${API_BASE}/jobs/${job.id}/summaries`)
        ]))
      )
      setExecutions((prev) => {
        const nextExecutions = { ...prev }
        responses.forEach((responsePair, index) => {
          nextExecutions[jobsList[index].id] = responsePair[0].data
        })
        return nextExecutions
      })
      setSummaries((prev) => {
        const nextSummaries = { ...prev }
        responses.forEach((responsePair, index) => {
          nextSummaries[jobsList[index].id] = responsePair[1].data
        })
        return nextSummaries
      })
    } catch (error) {
      console.error('Error preloading execution counts:', error)
    }
  }

  const toggleExecutions = async (jobId) => {
    const isExpanded = !!expandedExecutions[jobId]
    if (isExpanded) {
      setExpandedExecutions({ ...expandedExecutions, [jobId]: false })
      return
    }

    setExpandedExecutions({ ...expandedExecutions, [jobId]: true })
    if (!summaries[jobId]) {
      await loadExecutions(jobId)
    }
  }

  const getJobStats = (jobId) => {
    const jobExecutions = Array.isArray(executions[jobId]) ? executions[jobId] : []
    const jobSummaries = Array.isArray(summaries[jobId]) ? summaries[jobId] : []
    const inputTokens = jobSummaries.reduce((total, summary) => total + (summary.input_tokens || 0), 0)
    const outputTokens = jobSummaries.reduce((total, summary) => total + (summary.output_tokens || 0), 0)
    const tweetsAnalyzed = jobSummaries.reduce((total, summary) => {
      if (summary.raw_data && typeof summary.raw_data.count === 'number') {
        return total + summary.raw_data.count
      }
      return total + (summary.tweets_count || 0)
    }, 0)
    return {
      inputTokens,
      outputTokens,
      tweetsAnalyzed,
      runCount: jobExecutions.length
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

    const remainingRuns = getPlaygroundRemaining()
    if (remainingRuns <= 0) {
      alert('Playground limit reached. Please try again later.')
      return
    }

    recordPlaygroundRun()
    
    setTestLoading(true)
    setTestResult(null)
    try {
      const topics = testData.topics.split(',').map(t => t.trim()).filter(t => t)
      const response = await axios.post(`${API_BASE}/monitoring/test`, {
        x_username: testData.x_username.trim(),
        hours_back: parseInt(testData.hours_back) || 24,
        topics: topics,
        language: testData.language
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

  const languageOptions = [
    { value: 'zh', label: '中文' },
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Español' },
    { value: 'fr', label: 'Français' },
    { value: 'de', label: 'Deutsch' },
    { value: 'ja', label: '日本語' },
    { value: 'ko', label: '한국어' },
    { value: 'pt', label: 'Português' },
    { value: 'ru', label: 'Русский' },
    { value: 'it', label: 'Italiano' },
    { value: 'ar', label: 'العربية' },
    { value: 'hi', label: 'हिन्दी' },
    { value: 'id', label: 'Bahasa Indonesia' },
    { value: 'tr', label: 'Türkçe' },
    { value: 'vi', label: 'Tiếng Việt' },
    { value: 'th', label: 'ไทย' },
    { value: 'nl', label: 'Nederlands' }
  ]

  const playgroundRemaining = getPlaygroundRemaining()

  return (
    <>
      <Navbar
        onShowAuth={() => setShowAuthModal(true)}
        onToggleMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
        onShowProfile={onShowProfile}
      />
      <div className="app-layout">
        {/* Left Sidebar */}
        {mobileMenuOpen && <div className="mobile-menu-overlay" onClick={() => setMobileMenuOpen(false)} />}
        <div className={`sidebar ${mobileMenuOpen ? 'open' : ''}`}>
          <button 
            className={`sidebar-item ${activeView === 'playground' ? 'active' : ''}`}
            onClick={() => {
              setActiveView('playground')
              setMobileMenuOpen(false)
            }}
          >
            <TestTube size={20} />
            <span>Playground</span>
          </button>
          <button 
            className={`sidebar-item ${activeView === 'tasks' ? 'active' : ''}`}
            onClick={() => {
              setActiveView('tasks')
              setMobileMenuOpen(false)
            }}
          >
            <Clock size={20} />
            <span>Agentic Tasks</span>
          </button>
        </div>

        {/* Main Content Area */}
        <div className="main-content">
          <div className="main-content-inner">
            {activeView === 'tasks' && (
              <div className="jobs-container">
                {(jobs.length > 0 || showAddJob) && (
                  <div className="jobs-header">
                    <div className="section-title">
                      <h2>Agentic Tasks</h2>
                      <div className="section-hint">
                        Beta limit: up to 5 scheduled tasks per account.
                      </div>
                    </div>
                    <button
                      className="btn-primary add-task-cta"
                      onClick={() => setShowAddJob(!showAddJob)}
                      disabled={jobs.length >= MAX_TASKS_PER_USER}
                      title={jobs.length >= MAX_TASKS_PER_USER ? 'Maximum 5 tasks allowed.' : undefined}
                    >
                      <Plus size={18} />
                      Add Task
                    </button>
                  </div>
                )}

                {showAddJob && (
                  <div className="card add-job-card">
                    <h3>Add New Scheduled Task</h3>
                    <div className="form-group">
                      <label>
                        <User size={16} />
                        X Username
                      </label>
                      <input
                        type="text"
                        placeholder="elonmusk (without @)"
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
                        Topics
                      </label>
                      <input
                        type="text"
                        placeholder="AI, technology, space (comma-separated)"
                        value={newJob.topics}
                        onChange={(e) => setNewJob({ ...newJob, topics: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>
                        Language
                      </label>
                      <select
                        value={newJob.language}
                        onChange={(e) => setNewJob({ ...newJob, language: e.target.value })}
                      >
                        {languageOptions.map(opt => (
                          <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group form-group-distribution">
                      <label>
                        <Share2 size={16} />
                        Distribution Channel
                      </label>
                      <div className="option-row">
                        <label className="option-item">
                          <input
                            type="checkbox"
                            checked={newJob.send_email}
                            onChange={(e) => setNewJob({ ...newJob, send_email: e.target.checked })}
                          />
                          <span>
                            <Mail size={16} />
                            Email — send to {user?.email}
                          </span>
                        </label>
                        <label className="option-item">
                          <input
                            type="checkbox"
                            checked={newJob.send_telegram}
                            onChange={(e) => {
                              const checked = e.target.checked
                              setNewJob({
                                ...newJob,
                                send_telegram: checked,
                                telegram_target_ids: checked ? newJob.telegram_target_ids : []
                              })
                            }}
                          />
                          <span>
                            <Send size={16} />
                            Telegram — send to selected targets
                          </span>
                        </label>
                        {newJob.send_telegram && telegramTargetsForUser.length > 0 && (
                          <div className="telegram-targets">
                            {telegramTargetsForUser.map((target) => (
                              <label key={target.id} className="telegram-target-item">
                                <input
                                  type="checkbox"
                                  checked={newJob.telegram_target_ids.includes(target.id)}
                                  onChange={(e) => {
                                    const isChecked = e.target.checked
                                    const nextIds = isChecked
                                      ? [...newJob.telegram_target_ids, target.id]
                                      : newJob.telegram_target_ids.filter((id) => id !== target.id)
                                    setNewJob({
                                      ...newJob,
                                      send_telegram: true,
                                      telegram_target_ids: nextIds
                                    })
                                  }}
                                />
                                <span>{formatTelegramTargetLabel(target)}</span>
                              </label>
                            ))}
                          </div>
                        )}
                        {newJob.send_telegram && telegramTargetsForUser.length === 0 && (
                          <div className="telegram-warning">
                            No Telegram target set.{' '}
                            <button type="button" onClick={onShowProfile}>Bind now</button>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="form-actions form-actions-divider">
                      <button className="btn-secondary" onClick={() => setShowAddJob(false)}>
                        Cancel
                      </button>
                      <button className="btn-primary" onClick={addJob}>
                        Create Task
                      </button>
                    </div>
                  </div>
                )}

                {jobs.length === 0 && !showAddJob ? (
                  <div className="empty-state-centered">
                    <div className="empty-state-icon">
                      <Clock size={32} />
                    </div>
                    {user ? (
                      <>
                        <h3>Create your first scheduled task</h3>
                        <p>Automatically monitor X accounts and receive AI summaries</p>
                        <button className="btn-primary" onClick={() => setShowAddJob(true)}>
                          <Plus size={18} />
                          Add Task
                        </button>
                      </>
                    ) : (
                      <>
                        <h3>Agentic Tasks</h3>
                        <p>Automatically track X accounts and get AI summaries delivered on schedule</p>
                        <button className="btn-primary" onClick={() => setShowAuthModal(true)}>
                          Login / Register
                        </button>
                      </>
                    )}
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
                    <Zap size={18} />
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
                <div className="history-stats">
                  {(() => {
                    const stats = getJobStats(job.id)
                    return (
                      <>
                        <span>Input tokens: {stats.inputTokens}</span>
                        <span>Output tokens: {stats.outputTokens}</span>
                        <span>Tweets analyzed: {stats.tweetsAnalyzed}</span>
                        <button
                          className="btn-link stats-link"
                          onClick={() => toggleExecutions(job.id)}
                        >
                          Job runs: {stats.runCount}
                        </button>
                      </>
                    )
                  })()}
                </div>
                {expandedExecutions[job.id] && executions[job.id] && (
                  <div className="executions">
                            {(Array.isArray(executions[job.id]) ? executions[job.id] : [executions[job.id]])
                              .filter(e => e)
                              .map((execution, idx) => {
                                const executionSummaries = (Array.isArray(summaries[job.id]) ? summaries[job.id] : [summaries[job.id]])
                                  .filter(s => s && s.execution_id === execution.id)
                                return (
                                  <div key={execution.id || idx} className="execution-card">
                                    <div className="execution-header">
                                      <span className="execution-status">{execution.status}</span>
                                      <span className="execution-date">
                                        {execution.completed_at
                                          ? new Date(execution.completed_at).toLocaleString()
                                          : new Date(execution.started_at).toLocaleString()}
                                      </span>
                                    </div>
                                    <div className="execution-meta">
                                      <span>Tweets: {execution.tweets_fetched}</span>
                                      {execution.error_message && (
                                        <span className="execution-error">{execution.error_message}</span>
                                      )}
                                    </div>
                                    {executionSummaries.length > 0 && (
                                      <div className="execution-summaries">
                                        {executionSummaries.map((summary) => (
                                          <div key={summary.id} className="execution-summary">
                                            <div className="execution-summary-header">
                                              <span className="execution-summary-date">
                                                {new Date(summary.created_at).toLocaleString()}
                                              </span>
                                            </div>
                                            <div className="summary-content">
                                              {normalizeSummary(summary.content)}
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                )
                              })}
                          </div>
                        )}
              </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'playground' && (
              <div className="test-container">
                <div className="jobs-header">
                  <div className="section-title">
                    <h2>Instant summary</h2>
                  </div>
                </div>
                <div className="card test-card">
                  <div className="form-group">
                    <label>
                      <User size={16} />
                      X Username
                    </label>
                    <input
                      type="text"
                      placeholder="elonmusk (without @)"
                      value={testData.x_username}
                      onChange={(e) => setTestData({ ...testData, x_username: e.target.value })}
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <Clock size={16} />
                      Time range
                    </label>
                    <input
                      type="number"
                      placeholder="24"
                      min="1"
                      max="24"
                      value={testData.hours_back}
                      onChange={(e) => setTestData({ ...testData, hours_back: e.target.value })}
                    />
                    <small>How many hours back to search (1-24 hours)</small>
                  </div>

                  <div className="form-group">
                    <label>
                      <Hash size={16} />
                      Topics
                    </label>
                    <input
                      type="text"
                      placeholder="AI, technology, space (comma-separated)"
                      value={testData.topics}
                      onChange={(e) => setTestData({ ...testData, topics: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>
                      Language
                    </label>
                    <select
                      value={testData.language}
                      onChange={(e) => setTestData({ ...testData, language: e.target.value })}
                    >
                      {languageOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-actions">
                    <button
                      className="btn-primary"
                      onClick={runTest}
                      disabled={testLoading || playgroundRemaining <= 0}
                    >
                      {testLoading ? 'Running...' : (playgroundRemaining <= 0 ? 'Limit Reached' : 'Run')}
                    </button>
                  </div>
                  <div className="form-helper">
                    Beta limit: up to 10 playground runs per 24 hours on this device.
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
                          {normalizeSummary(testResult.summary)}
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
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

function AppContent() {
  const { user, loading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#ffffff'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '3px solid #f3f3f3',
            borderTop: '3px solid #000',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }}></div>
          <p style={{ color: '#666' }}>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <MainApp
        showAuthModal={showAuthModal}
        setShowAuthModal={setShowAuthModal}
        onShowProfile={() => setShowProfileModal(true)}
      />
      {showAuthModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#fff',
            borderRadius: '8px',
            padding: '0',
            maxWidth: '420px',
            width: '90%',
            maxHeight: '90vh',
            overflow: 'auto',
            position: 'relative'
          }}>
            <button
              onClick={() => setShowAuthModal(false)}
              style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#666',
                zIndex: 10
              }}
            >
              ×
            </button>
            <AuthFlow onSuccess={() => setShowAuthModal(false)} />
          </div>
        </div>
      )}
      {showProfileModal && <Profile onClose={() => setShowProfileModal(false)} />}
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App
