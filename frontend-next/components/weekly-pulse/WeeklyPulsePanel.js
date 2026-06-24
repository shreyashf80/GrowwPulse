import ThemeCard from './ThemeCard';
import styles from './WeeklyPulsePanel.module.css';

export default function WeeklyPulsePanel({ data }) {
  if (!data || !data.themes) return null;

  const totalReviews = data.themes.reduce((s, t) => s + t.review_count, 0);

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `groww_pulse_${data.iso_week}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className={styles.header}>
        <h2>Top Weekly Themes</h2>
        <button className={styles.exportBtn} onClick={handleExport}>
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>download</span>
          EXPORT ALL
        </button>
      </div>

      <div className={styles.grid}>
        {data.themes.map((theme, idx) => {
          const isWide = idx === data.themes.length - 1 && data.themes.length % 2 !== 0;
          return (
            <ThemeCard
              key={idx}
              theme={theme}
              rank={idx + 1}
              totalReviews={totalReviews}
              isWide={isWide}
            />
          );
        })}
      </div>
    </>
  );
}
