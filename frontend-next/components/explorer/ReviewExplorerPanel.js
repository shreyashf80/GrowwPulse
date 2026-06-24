'use client';
import { useState, useMemo } from 'react';
import styles from './ReviewExplorerPanel.module.css';

const THEME_RULES = [
  { name: 'Trading Issues',        color: 'red',   test: r => r.rating <= 2 && /trad|execut|order|lag|stuck|glitch/i.test(r.text) },
  { name: 'Poor Customer Support', color: 'red',   test: r => r.rating <= 2 && /support|customer.?care|respond|agent|call/i.test(r.text) },
  { name: 'Feature Requests',      color: 'amber', test: r => /add|please|feature|request|indicator|option|allow|chart/i.test(r.text) },
  { name: 'Good Investment App',   color: 'green', test: r => r.rating >= 4 && /invest|good|best|excel|great|love|sip|mutual/i.test(r.text) },
  { name: 'Easy Interface',        color: 'green', test: r => r.rating >= 4 && /easy|simple|ui|interface|beginner|use/i.test(r.text) },
];

function inferTheme(review) {
  for (const rule of THEME_RULES) {
    if (rule.test(review)) return { name: rule.name, color: rule.color };
  }
  if (review.rating >= 4) return { name: 'Good Investment App', color: 'green' };
  if (review.rating <= 2) return { name: 'Trading Issues', color: 'red' };
  return { name: 'Feature Requests', color: 'amber' };
}

const PER_PAGE = 10;

export default function ReviewExplorerPanel({ reviews }) {
  const [search, setSearch]       = useState('');
  const [activeStars, setActive]  = useState(new Set());
  const [version, setVersion]     = useState('all');
  const [sort, setSort]           = useState('helpful');
  const [page, setPage]           = useState(1);

  // Compute stats
  const dist = useMemo(() => {
    const counts = { 5:0, 4:0, 3:0, 2:0, 1:0 };
    reviews.forEach(r => { if (counts[r.rating] !== undefined) counts[r.rating]++; });
    const total = reviews.length || 1;
    return [5,4,3,2,1].map(star => ({
      star,
      pct: ((counts[star] / total) * 100).toFixed(0)
    }));
  }, [reviews]);

  const versions = useMemo(() => {
    return [...new Set(reviews.map(r => r.app_version).filter(Boolean))].sort().reverse();
  }, [reviews]);

  // Filter
  const filtered = useMemo(() => {
    let res = reviews;
    if (activeStars.size > 0) res = res.filter(r => activeStars.has(r.rating));
    if (version !== 'all')    res = res.filter(r => r.app_version === version);
    if (search.trim()) {
      const q = search.toLowerCase();
      res = res.filter(r => r.text.toLowerCase().includes(q) || r.author.toLowerCase().includes(q));
    }
    if (sort === 'helpful') res = [...res].sort((a,b) => b.thumbs_up - a.thumbs_up);
    else if (sort === 'newest')  res = [...res].sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
    else res = [...res].sort((a,b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    return res;
  }, [reviews, activeStars, version, search, sort]);

  const toggleStar = (star) => {
    setActive(prev => {
      const next = new Set(prev);
      if (next.has(star)) next.delete(star); else next.add(star);
      return next;
    });
    setPage(1);
  };

  const pages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const currentReviews = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE);

  return (
    <div>
      {/* Sticky Filter Bar */}
      <div className={`glass-card ${styles.filterBar}`}>
        <div className={styles.rowTop}>
          <div className={styles.searchWrap}>
            <span className="material-symbols-outlined">search</span>
            <input
              type="search"
              placeholder="Search reviews by keyword..."
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1); }}
              className={styles.searchInput}
            />
          </div>
          <div className={styles.stars}>
            {[5,4,3,2,1].map(star => (
              <button
                key={star}
                className={`${styles.starBtn} ${activeStars.has(star) ? styles.active : ''}`}
                onClick={() => toggleStar(star)}
              >
                {star} <span className="material-symbols-outlined icon-filled">star</span>
              </button>
            ))}
          </div>
        </div>
        <div className={styles.rowBottom}>
          <select value={version} onChange={e => { setVersion(e.target.value); setPage(1); }} className={styles.select}>
            <option value="all">All Versions</option>
            {versions.map(v => <option key={v} value={v}>v{v}</option>)}
          </select>
          <select value={sort} onChange={e => { setSort(e.target.value); setPage(1); }} className={styles.select}>
            <option value="helpful">Sort: Most Helpful</option>
            <option value="newest">Sort: Newest</option>
            <option value="oldest">Sort: Oldest</option>
          </select>
          <button className={styles.dateBtn}>
            <span className="material-symbols-outlined">calendar_month</span> Date Range
          </button>
          <span className={styles.resultsCount}>Showing {filtered.length.toLocaleString()} reviews</span>
        </div>
      </div>

      {/* Distribution */}
      <div className={`glass-card ${styles.distSection}`}>
        <div className={styles.distHeader}>
          <h3>Rating Distribution</h3>
          <span>Last 30 Days</span>
        </div>
        <div className={styles.distTrack}>
          {dist.map(d => (
            <div
              key={d.star}
              className={`${styles.distSegment} ${styles['s'+d.star]}`}
              style={{ width: `${d.pct}%` }}
              title={`${d.star}★: ${d.pct}%`}
              onClick={() => toggleStar(d.star)}
            >
              {d.pct}%
            </div>
          ))}
        </div>
      </div>

      {/* Feed */}
      <div className={styles.feed}>
        {currentReviews.length === 0 ? (
          <div className={styles.empty}>No reviews match your filters.</div>
        ) : (
          currentReviews.map(r => <ReviewCard key={r.review_id} review={r} />)
        )}
      </div>

      {/* Pagination */}
      <div className={styles.pagination}>
        <button disabled={page <= 1} onClick={() => { setPage(p=>p-1); window.scrollTo({top:0,behavior:'smooth'}); }}>
          <span className="material-symbols-outlined">arrow_back</span> Prev
        </button>
        <span>Page {page} of {pages}</span>
        <button disabled={page >= pages} onClick={() => { setPage(p=>p+1); window.scrollTo({top:0,behavior:'smooth'}); }}>
          Next <span className="material-symbols-outlined">arrow_forward</span>
        </button>
      </div>
    </div>
  );
}

function ReviewCard({ review }) {
  const [expanded, setExpanded] = useState(false);
  const theme = inferTheme(review);
  const isPos = review.rating >= 4;
  const isNeg = review.rating <= 2;
  const sentiment = isPos ? 'pos' : isNeg ? 'neg' : 'neu';
  
  const initial = (review.author || '?')[0].toUpperCase();
  const date = new Date(review.timestamp).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
  const thumbs = review.thumbs_up >= 1000 ? `${(review.thumbs_up/1000).toFixed(1)}K` : review.thumbs_up;
  const actionLabel = isPos ? 'Thank User' : isNeg ? 'Escalate' : 'Reply';
  const actionIcon  = isPos ? 'thumb_up_alt' : isNeg ? 'flag' : 'reply';
  const needsClamp  = review.text.length > 200;

  return (
    <div className={`glass-card ${styles.reviewCard} ${styles[sentiment]}`}>
      <div className={styles.reviewTop}>
        <div className={styles.authorRow}>
          <div className={`${styles.avatar} ${styles[sentiment]}`}>{initial}</div>
          <div>
            <h4 className={styles.authorName}>{review.author}</h4>
            <div className={styles.starsRow}>
              {[1,2,3,4,5].map(i => (
                <span key={i} className={`material-symbols-outlined ${i <= review.rating ? 'icon-filled' : ''} ${i <= review.rating ? styles['star'+sentiment] : styles.starEmpty}`}>star</span>
              ))}
            </div>
          </div>
        </div>
        <div className={styles.reviewRight}>
          <span className={`${styles.themePill} ${styles[theme.color]}`}>{theme.name}</span>
          {review.app_version && <span className={styles.badge}>v{review.app_version}</span>}
          <span className={styles.badge} style={{ opacity: 0.6 }}>{date}</span>
        </div>
      </div>

      <div>
        <p className={`${styles.reviewText} ${!expanded && needsClamp ? styles.clamped : ''}`}>{review.text}</p>
        {needsClamp && (
          <button className={styles.readMore} onClick={() => setExpanded(e => !e)}>
            {expanded ? 'Show less' : 'Read more'}
          </button>
        )}
      </div>

      <div className={styles.footer}>
        <button title="Helpful">
          <span className="material-symbols-outlined">thumb_up</span>
          <span className={review.thumbs_up >= 1000 ? styles.highThumbs : ''}>{thumbs}</span>
        </button>
        <button title={actionLabel}>
          <span className="material-symbols-outlined">{actionIcon}</span>
          {actionLabel}
        </button>
      </div>
    </div>
  );
}
