// chuyou-tokens.jsx — Shared tokens, icons, and small components for 出游助手

// ───────── Design Tokens ─────────
const CY = {
  green:   '#1A8870',   // primary
  greenD:  '#0F5E4D',
  greenL:  '#E8F2EC',   // tag bg / soft surfaces
  greenLS: '#F2F7F4',   // very soft bg
  greenLine:'#D5E8DD',
  bg:      '#FAFBFA',
  card:    '#FFFFFF',
  text:    '#1F2A2A',
  textSub: '#4B5563',
  muted:   '#9CA3AF',
  border:  '#EFEFEF',
  star:    '#F5B940',
  blueTag: '#E5F0FA',
  blueTxt: '#4A90C8',
  pinkTag: '#FCE8EC',
  pinkTxt: '#C8597A',
};

// ───────── Phone Status Bar (9:41) ─────────
function CYStatusBar({ dark = false }) {
  const c = dark ? '#fff' : '#000';
  return (
    <div style={{
      height: 44, padding: '0 22px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      fontFamily: '-apple-system, "SF Pro", system-ui',
      position: 'relative', zIndex: 10, flexShrink: 0,
    }}>
      <span style={{ fontSize: 16, fontWeight: 600, color: c }}>9:41</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        {/* signal */}
        <svg width="17" height="11" viewBox="0 0 17 11">
          <rect x="0" y="7" width="3" height="4" rx="0.6" fill={c}/>
          <rect x="4.5" y="5" width="3" height="6" rx="0.6" fill={c}/>
          <rect x="9" y="2.5" width="3" height="8.5" rx="0.6" fill={c}/>
          <rect x="13.5" y="0" width="3" height="11" rx="0.6" fill={c}/>
        </svg>
        {/* wifi */}
        <svg width="16" height="11" viewBox="0 0 16 11">
          <path d="M8 2.5C10.3 2.5 12.4 3.4 13.9 4.9L15 3.8C13.2 2 10.7 0.8 8 0.8C5.3 0.8 2.8 2 1 3.8L2.1 4.9C3.6 3.4 5.7 2.5 8 2.5Z" fill={c}/>
          <path d="M8 5.8C9.4 5.8 10.6 6.3 11.5 7.2L12.6 6.1C11.3 4.9 9.7 4.1 8 4.1C6.3 4.1 4.7 4.9 3.4 6.1L4.5 7.2C5.4 6.3 6.6 5.8 8 5.8Z" fill={c}/>
          <circle cx="8" cy="9.5" r="1.4" fill={c}/>
        </svg>
        {/* battery */}
        <svg width="25" height="12" viewBox="0 0 25 12">
          <rect x="0.5" y="0.5" width="21" height="11" rx="3" stroke={c} strokeOpacity="0.4" fill="none"/>
          <rect x="2" y="2" width="18" height="8" rx="1.5" fill={c}/>
          <path d="M23 4v4c.7-.2 1.3-1.1 1.3-2S23.7 4.2 23 4z" fill={c} fillOpacity="0.5"/>
        </svg>
      </div>
    </div>
  );
}

// ───────── Phone Frame ─────────
function Phone({ children, bg='#fff' }) {
  return (
    <div className="phone-typo" style={{
      width: 393, height: 852, borderRadius: 48,
      background: bg, overflow: 'hidden', position: 'relative',
      boxShadow: '0 30px 60px rgba(0,0,0,0.14), 0 0 0 1px rgba(0,0,0,0.08)',
      fontFamily: '"PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif',
      WebkitFontSmoothing: 'antialiased',
      MozOsxFontSmoothing: 'grayscale',
      letterSpacing: '0.01em',
      display: 'flex', flexDirection: 'column',
    }}>
      {children}
      {/* home indicator */}
      <div style={{
        position: 'absolute', bottom: 8, left: '50%', transform: 'translateX(-50%)',
        width: 134, height: 5, borderRadius: 100, background: 'rgba(0,0,0,0.85)', zIndex: 60,
      }} />
    </div>
  );
}

// ───────── Header (Back/Title/Action) ─────────
function NavBar({ title, subtitle, onBack, action, leftBack=true }) {
  return (
    <div style={{
      padding: '6px 18px 14px',
      display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
      borderBottom: `1px solid ${CY.border}`, background: '#fff', flexShrink: 0,
    }}>
      <div style={{ width: 32, paddingTop: 4 }}>
        {leftBack && (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M15 5l-7 7 7 7" stroke={CY.text} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )}
      </div>
      <div style={{ flex: 1, textAlign: 'center' }}>
        <div style={{ fontSize: 19, fontWeight: 800, color: CY.text }}>{title}</div>
        {subtitle && <div style={{ fontSize: 13, color: CY.muted, marginTop: 4 }}>{subtitle}</div>}
      </div>
      <div style={{ width: 32, textAlign: 'right', paddingTop: 4 }}>{action}</div>
    </div>
  );
}

// ───────── Search Icon ─────────
const SearchIcon = ({ s=22, c=CY.text }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
    <circle cx="11" cy="11" r="7.5" stroke={c} strokeWidth="2"/>
    <path d="M17 17l4 4" stroke={c} strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

// ───────── Star ─────────
const Star = ({ s=14 }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill={CY.star}>
    <path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.9-6.2-3.3-6.2 3.3 1.2-6.9-5-4.9 6.9-1L12 2z"/>
  </svg>
);

// ───────── Pin ─────────
const Pin = ({ s=14, c=CY.green }) => (
  <svg width={s} height={s} viewBox="0 0 24 24" fill={c}>
    <path d="M12 2C7.6 2 4 5.6 4 10c0 6 8 12 8 12s8-6 8-12c0-4.4-3.6-8-8-8zm0 11a3 3 0 110-6 3 3 0 010 6z"/>
  </svg>
);

// ───────── Bottom Tab Bar (4 tabs) ─────────
function TabBar({ active='home' }) {
  const tabs = [
    { id:'home',     label:'出游',
      i:(a)=>(<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M5 7l7-4 7 4v10a2 2 0 01-2 2H7a2 2 0 01-2-2V7z" stroke={a?CY.green:'#9AA3A8'} strokeWidth="2" fill={a?CY.greenL:'none'} strokeLinejoin="round"/>
        <path d="M10 19v-5h4v5" stroke={a?CY.green:'#9AA3A8'} strokeWidth="2" strokeLinecap="round"/>
        <circle cx="8" cy="8" r="0.9" fill={a?CY.green:'#9AA3A8'}/>
      </svg>) },
    { id:'discover', label:'发现',
      i:(a)=>(<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke={a?CY.green:'#9AA3A8'} strokeWidth="2"/>
        <path d="M15.5 8.5l-1.8 5.2-5.2 1.8 1.8-5.2 5.2-1.8z" fill={a?CY.green:'#9AA3A8'}/>
      </svg>) },
    { id:'chat',     label:'咨询',
      i:(a)=>(<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M4 5h16v11H8l-4 4V5z" stroke={a?CY.green:'#9AA3A8'} strokeWidth="2" fill={a?CY.greenL:'none'} strokeLinejoin="round"/>
      </svg>) },
    { id:'me',       label:'我的',
      i:(a)=>(<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="8" r="4" stroke={a?CY.green:'#9AA3A8'} strokeWidth="2" fill={a?CY.greenL:'none'}/>
        <path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" stroke={a?CY.green:'#9AA3A8'} strokeWidth="2" strokeLinecap="round" fill="none"/>
      </svg>) },
  ];
  return (
    <div style={{
      background:'#fff', borderTop:`1px solid ${CY.border}`,
      paddingTop:8, paddingBottom:30,
      display:'flex', flexShrink:0,
    }}>
      {tabs.map(t => {
        const a = active === t.id;
        return (
          <div key={t.id} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
            {t.i(a)}
            <span style={{ fontSize:11, fontWeight: a?700:500, color: a?CY.green:'#9AA3A8' }}>{t.label}</span>
          </div>
        );
      })}
    </div>
  );
}

// ───────── Tag chip ─────────
function Chip({ label, color='green', size='md' }) {
  const map = {
    green: { bg: CY.greenL, c: CY.green },
    blue:  { bg: CY.blueTag, c: CY.blueTxt },
    pink:  { bg: CY.pinkTag, c: CY.pinkTxt },
    plain: { bg: '#F3F4F6', c: '#6B7280' },
  };
  const { bg, c } = map[color];
  return (
    <span style={{
      display:'inline-flex', alignItems:'center',
      padding: size==='sm' ? '3px 8px' : '4px 10px',
      borderRadius: 6, fontSize: size==='sm' ? 11 : 12, fontWeight: 500,
      background: bg, color: c, whiteSpace:'nowrap',
    }}>{label}</span>
  );
}

// ───────── Robot mascot SVG ─────────
function RobotMascot({ size=80 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" fill="none">
      {/* antenna */}
      <circle cx="50" cy="12" r="3" fill="#1A8870"/>
      <line x1="50" y1="14" x2="50" y2="22" stroke="#1A8870" strokeWidth="2.5"/>
      {/* head */}
      <ellipse cx="50" cy="46" rx="28" ry="26" fill="#0F5E4D"/>
      {/* face shine */}
      <ellipse cx="42" cy="38" rx="12" ry="9" fill="#1A8870" opacity="0.5"/>
      {/* eyes */}
      <circle cx="40" cy="46" r="6" fill="#fff"/>
      <circle cx="60" cy="46" r="6" fill="#fff"/>
      <circle cx="41" cy="47" r="3.5" fill="#1B4D7E"/>
      <circle cx="61" cy="47" r="3.5" fill="#F5B940"/>
      <circle cx="42" cy="46" r="1" fill="#fff"/>
      <circle cx="62" cy="46" r="1" fill="#fff"/>
      {/* mouth */}
      <path d="M44 56c2 2 4 3 6 3s4-1 6-3" stroke="#fff" strokeWidth="1.6" strokeLinecap="round" fill="none"/>
      {/* ears */}
      <circle cx="20" cy="46" r="4.5" fill="#1A8870"/>
      <circle cx="80" cy="46" r="4.5" fill="#1A8870"/>
      {/* body */}
      <ellipse cx="50" cy="82" rx="22" ry="13" fill="#fff" stroke="#D8E5DE" strokeWidth="1.2"/>
      <circle cx="50" cy="80" r="5" fill="#E8F2EC"/>
      <path d="M50 76v6M50 80c-1.4 0-2.5 1.1-2.5 2.5" stroke="#1A8870" strokeWidth="1.4" strokeLinecap="round" fill="none"/>
      {/* arms */}
      <ellipse cx="26" cy="78" rx="5" ry="6" fill="#fff" stroke="#D8E5DE" strokeWidth="1"/>
      <ellipse cx="74" cy="78" rx="5" ry="6" fill="#fff" stroke="#D8E5DE" strokeWidth="1"/>
    </svg>
  );
}

// ───────── Section title row ─────────
function SectionTitle({ title, more, onMore }) {
  return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom: 10 }}>
      <div style={{ fontSize: 16, fontWeight: 700, color: CY.text }}>{title}</div>
      {more && (
        <div onClick={onMore} style={{ fontSize: 13, color: CY.muted, display:'flex', alignItems:'center', gap:2 }}>
          {more} <span style={{ fontSize:14 }}>›</span>
        </div>
      )}
    </div>
  );
}

// ───────── Image placeholder w/ photo URL ─────────
function Photo({ src, alt='', style }) {
  return <img src={src} alt={alt}
    style={{ width:'100%', height:'100%', objectFit:'cover', display:'block', ...style }} />;
}

Object.assign(window, {
  CY, CYStatusBar, Phone, NavBar, SearchIcon, Star, Pin,
  TabBar, Chip, RobotMascot, SectionTitle, Photo,
});
