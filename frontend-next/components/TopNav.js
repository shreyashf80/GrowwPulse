'use client';
import styles from './TopNav.module.css';

const WEEKS = ['2026-W24', '2026-W23', '2026-W22', '2026-W21'];

export default function TopNav({ activeTab, onTabChange, selectedWeek, onWeekChange }) {
  return (
    <nav className={styles.topnav}>
      <div className={styles.left}>
        {/* Logo */}
        <div className={styles.logo}>
          <span className="material-symbols-outlined icon-filled" style={{ fontSize: 22, color: 'var(--color-primary)' }}>monitoring</span>
          <span>Groww Review Pulse</span>
        </div>

        {/* Tab switcher */}
        <div className={styles.tabs} role="tablist">
          {['pulse', 'explorer'].map(tab => (
            <button
              key={tab}
              role="tab"
              aria-selected={activeTab === tab}
              className={`${styles.tabBtn} ${activeTab === tab ? styles.active : ''}`}
              onClick={() => onTabChange(tab)}
            >
              {tab === 'pulse' ? 'Weekly Pulse' : 'Review Explorer'}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.right}>
        {/* Week selector */}
        <label className={styles.weekSelector}>
          <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--color-on-surface-muted)' }}>calendar_today</span>
          <select value={selectedWeek} onChange={e => onWeekChange(e.target.value)} aria-label="Select ISO week">
            {WEEKS.map(w => <option key={w} value={w}>{w}</option>)}
          </select>
          <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--color-on-surface-muted)' }}>expand_more</span>
        </label>

        <button className={styles.iconBtn} aria-label="Notifications">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button className={styles.iconBtn} aria-label="Settings">
          <span className="material-symbols-outlined">settings</span>
        </button>
        <div className={styles.avatar} role="img" aria-label="User profile">G</div>
      </div>
    </nav>
  );
}
