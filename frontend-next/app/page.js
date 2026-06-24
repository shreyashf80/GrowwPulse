'use client';
import { useState, useEffect } from 'react';
import TopNav from '../components/TopNav';
import Sidebar from '../components/Sidebar';
import HeroStats from '../components/weekly-pulse/HeroStats';
import WeeklyPulsePanel from '../components/weekly-pulse/WeeklyPulsePanel';
import PipelineStatus from '../components/weekly-pulse/PipelineStatus';
import EmailPreviewModal from '../components/weekly-pulse/EmailPreviewModal';
import ReviewExplorerPanel from '../components/explorer/ReviewExplorerPanel';
import styles from './page.module.css';

export default function Home() {
  const [activeTab, setActiveTab] = useState('pulse');
  const [week, setWeek] = useState('2026-W24');
  const [pulseData, setPulseData] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState(null);
  const [showEmailModal, setShowEmailModal] = useState(false);

  // Load pulse data
  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const res = await fetch(`/data/frontend_output.json`);
        const data = await res.json();
        setPulseData(data);
      } catch (err) {
        console.error('Failed to load pulse data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [week]);

  // Load reviews
  useEffect(() => {
    async function loadReviews() {
      try {
        const res = await fetch('/data/actual_reviews.json');
        const data = await res.json();
        setReviews(data);
      } catch (err) {
        console.error('Failed to load reviews', err);
      }
    }
    loadReviews();
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerateError(null);
    try {
      const res = await fetch('/api/regenerate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ week }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.details || 'Pipeline failed');
      }
      const data = await res.json();
      setPulseData(data);
    } catch (err) {
      console.error('Regeneration failed:', err);
      setGenerateError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <div className={styles.ambientBg} aria-hidden="true" />

      <TopNav
        activeTab={activeTab}
        onTabChange={setActiveTab}
        selectedWeek={week}
        onWeekChange={setWeek}
      />

      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onGenerateReport={handleGenerate}
        isGenerating={isGenerating}
      />

      <main className={styles.main}>
        {generateError && (
          <div className={styles.errorBanner}>
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>error</span>
            Regeneration failed: {generateError}
            <button onClick={() => setGenerateError(null)}>✕</button>
          </div>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '100px', color: 'var(--color-on-surface-muted)' }}>
            Loading data...
          </div>
        ) : activeTab === 'pulse' ? (
          <div role="tabpanel" className={styles.panel}>
            {pulseData && <HeroStats data={pulseData} />}
            <WeeklyPulsePanel data={pulseData} />
            {pulseData?.pipeline && (
              <PipelineStatus
                pipeline={pulseData.pipeline}
                email={pulseData.email}
                onPreviewEmail={() => setShowEmailModal(true)}
              />
            )}
          </div>
        ) : (
          <div role="tabpanel" className={styles.panel}>
            <ReviewExplorerPanel reviews={reviews} />
          </div>
        )}
      </main>

      <footer className={styles.footer}>
        <span>Powered by UMAP + HDBSCAN + Groq LLaMA 3.3 • Next.js App Router</span>
        <div className={styles.footerRight}>
          {pulseData?.pipeline && (
            <span>Last run: {new Date(pulseData.pipeline.run_timestamp).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
          )}
          <span className={styles.statusDot}>System Status: Healthy</span>
        </div>
      </footer>

      {showEmailModal && pulseData?.email && (
        <EmailPreviewModal
          email={pulseData.email}
          onClose={() => setShowEmailModal(false)}
        />
      )}
    </>
  );
}
