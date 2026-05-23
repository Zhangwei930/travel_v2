// zhoumi-screens.jsx — V3 简洁风 + 索引语言
// Clean cards, soft palette, with subtle "§ N° / NO.xxx" index typography as accent

// ── Design Tokens ─────────────────────────────────────────
const Z = {
  primary:  '#0D4F4A',   // 墨青绿
  primaryD: '#062E2B',
  accent:   '#FF6B35',   // 暖橙
  amber:    '#F4B942',
  mint:     '#4FD1C5',
  bg:       '#F5F1EB',
  card:     '#FFFFFF',
  text:     '#1A2E2C',
  text2:    '#3B4A40',
  muted:    '#8B9594',
  border:   '#E8E2D8',
  line:     '#EFEADF',
};

const SERIF = "'Noto Serif SC', 'Songti SC', serif";
const SANS  = "'Noto Sans SC', -apple-system, sans-serif";
const MONO  = "'JetBrains Mono', 'SF Mono', monospace";

// ── Data ──────────────────────────────────────────────────
const CITY = '乌鲁木齐';
const WEATHER = { temp: 22, cond: '晴', icon: '☀️', advice: '适合出游' };

const SCENES = [
  { id:'family', no:'01', label:'亲子游',  icon:'👨‍👩‍👧',  color:'#FF6B35', desc:'轻松不太累' },
  { id:'couple', no:'02', label:'情侣约会', icon:'💑',         color:'#EC4B85', desc:'拍照·夜游' },
  { id:'rainy',  no:'03', label:'雨天室内', icon:'☔️',         color:'#5B7CFA', desc:'博物馆·商场' },
  { id:'budget', no:'04', label:'低预算',   icon:'🪙',         color:'#4FD1C5', desc:'免费·Citywalk' },
  { id:'fish',   no:'05', label:'钓鱼',     icon:'🎣',         color:'#3E5C3A', desc:'水库·黄金时段' },
  { id:'photo',  no:'06', label:'拍照打卡', icon:'📸',         color:'#A855F7', desc:'地标·出片' },
  { id:'night',  no:'07', label:'夜游',     icon:'🌃',         color:'#1F2937', desc:'夜市·灯光' },
  { id:'walk',   no:'08', label:'Citywalk', icon:'🚶',         color:'#84CC16', desc:'慢走·人文' },
  { id:'old',    no:'09', label:'适老',     icon:'👵',         color:'#F4B942', desc:'轻量·无障碍' },
];

const NEARBY = [
  { id:1, no:'NO.001', name:'新疆博物馆',   cat:'博物馆·室内', dist:'1.2km', time:'2-3h', budget:'免费',    tags:['亲子','雨天','文化'],   img:'https://picsum.photos/seed/zn1/400/300', reason:'室内不受天气影响，了解新疆历史文化' },
  { id:2, no:'NO.002', name:'红山公园',     cat:'公园·登高',   dist:'2.4km', time:'1-2h', budget:'免费',    tags:['Citywalk','晨练'],      img:'https://picsum.photos/seed/zn2/400/300', reason:'乌鲁木齐市标，登高俯瞰城市' },
  { id:3, no:'NO.003', name:'柴窝堡水库',   cat:'水库·钓点',   dist:'48km',  time:'半日',  budget:'低预算',  tags:['钓鱼','自然','自驾'],   img:'https://picsum.photos/seed/zn3/400/300', reason:'周边知名钓点，鱼种丰富' },
  { id:4, no:'NO.004', name:'水磨沟公园',   cat:'公园·清晨',   dist:'3.8km', time:'2-3h', budget:'免费',    tags:['自然','亲子','晨练'],   img:'https://picsum.photos/seed/zn4/400/300', reason:'清晨适合散步，水景宜人' },
  { id:5, no:'NO.005', name:'国际大巴扎',   cat:'购物·文化',   dist:'4.1km', time:'2h',   budget:'中等',    tags:['美食','拍照','购物'],   img:'https://picsum.photos/seed/zn5/400/300', reason:'西域文化与美食荟萃' },
];

const ROUTES = [
  { id:1, no:'R-01', title:'亲子半日游',     tag:'亲子',     color:'#FF6B35', duration:'半日', budget:'低',  poi:3, img:'https://picsum.photos/seed/zr1/500/300', summary:'博物馆+本地餐饮+公园，全程室内/近距，孩子不累' },
  { id:2, no:'R-02', title:'柴窝堡钓鱼一日', tag:'钓鱼',     color:'#3E5C3A', duration:'一日', budget:'中',  poi:3, img:'https://picsum.photos/seed/zr2/500/300', summary:'清晨出发→水库下竿→中午岸边野餐→傍晚返程' },
  { id:3, no:'R-03', title:'情侣夜游线',     tag:'情侣',     color:'#EC4B85', duration:'夜晚', budget:'中',  poi:4, img:'https://picsum.photos/seed/zr3/500/300', summary:'红山夜景→大巴扎晚餐→咖啡店' },
  { id:4, no:'R-04', title:'低预算 Citywalk',tag:'Citywalk', color:'#4FD1C5', duration:'一日', budget:'免费',poi:5, img:'https://picsum.photos/seed/zr4/500/300', summary:'公园+老街+二道桥，全程公交可达' },
];

const PLAN_RESULT = {
  no:'PLAN-2026-0521',
  title:'柴窝堡钓鱼一日方案',
  summary:'根据天气与水况，今日为本周最佳钓鱼日。清晨出发、黄金时段下竿、傍晚返程。',
  totalBudget:'人均 80-180 元',
  totalTime:'约 9 小时',
  people:'2 人',
  weather:'☀️ 22° 晴',
  stops:[
    { idx:1, name:'柴窝堡水库（南岸）', cat:'水域·钓点', arrive:'07:00', stay:'4小时', budget:'入场 0 元', reason:'南岸早间日影适宜，水温较低，鲫鱼活跃', tip:'风向决定坐向，建议背风。蚊虫多需防虫液', transport:'自驾·约90分钟' },
    { idx:2, name:'岸边野餐区',         cat:'休整',     arrive:'11:30', stay:'1小时', budget:'30-50 元', reason:'风向背阴处搭折叠桌椅，避开正午阳光',     tip:'垃圾必须带走，严禁明火炊事',                 transport:'步行 200 m' },
    { idx:3, name:'达坂城风电场观景',   cat:'风景·返程', arrive:'15:00', stay:'1小时', budget:'免费',    reason:'回程顺路，巨型风车阵列拍照震撼',         tip:'路边停车注意车流；强风时段注意防风',         transport:'自驾·40分钟' },
  ],
  gearList:['钓竿×2','鱼饵(蚯蚓/玉米)','折叠椅','遮阳帽','防虫液','保温水壶','垃圾袋'],
  backup:'若清晨刮 4 级以上大风，改为水磨沟公园+室内活动。如水位变化无鱼讯，转点至下游小水库。',
  disclaimer:'营业、水位、限钓信息以官方/管理处实时通告为准。',
  sources:[
    { kind:'地图', t:'柴窝堡 POI · 路线' },
    { kind:'知识库', t:'钓鱼模板 R-02 · 已审核' },
    { kind:'天气', t:'实时气象 API' },
    { kind:'WebSearch', t:'今日限钓公告' },
  ],
};

const FAQ_QUICK = ['钓点限钓吗？','需要钓鱼证吗？','停车方便吗？','下雨改去哪？','适合带孩子吗？','傍晚还能玩什么？'];

const CHAT_HISTORY = [
  { role:'bot', text:'你好👋 我是周密出游助手，可以帮你规划路线、查询地点、解决出游疑问。' },
  { role:'bot', chips: FAQ_QUICK.slice(0,4) },
  { role:'user', text:'柴窝堡水库这周末适合钓鱼吗？' },
  { role:'bot', text:'**本周末（5/22-5/23）适合**。\n\n根据当前数据：\n• 周六：☀️ 21° 东北风 2 级，水温适中\n• 周日：☁️ 19° 风力增强 4 级，建议改至周六\n\n推荐时段 05:30–10:00 清晨，鱼类觅食活跃。', sources:[{k:'气象',v:'气象 API'},{k:'知识库',v:'钓鱼模板 R-02'}] },
];

// ── Visual Primitives ─────────────────────────────────────

// Index-style section header — subtle but distinctive
function Sec({ no, title, sub, action }) {
  return (
    <div style={{ display:'flex', alignItems:'flex-end', justifyContent:'space-between', marginBottom:11 }}>
      <div style={{ display:'flex', alignItems:'baseline', gap:8 }}>
        <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, fontWeight:700, letterSpacing:0.5, paddingBottom:1 }}>§ {no}</span>
        <div>
          <div style={{ fontFamily:SERIF, fontSize:15, fontWeight:800, color:Z.text, lineHeight:1.2 }}>{title}</div>
          {sub && <div style={{ fontSize:10.5, color:Z.muted, marginTop:1 }}>{sub}</div>}
        </div>
      </div>
      {action && <span style={{ fontSize:11.5, color:Z.primary, fontWeight:600, cursor:'pointer' }}>{action} ›</span>}
    </div>
  );
}

function Tag({ label, color, small }) {
  const c = color || Z.primary;
  return (
    <span style={{
      display:'inline-flex', alignItems:'center',
      padding: small ? '2px 7px' : '3px 8px',
      borderRadius:6, fontSize: small ? 10 : 11, fontWeight:600,
      background: c+'14', color: c, whiteSpace:'nowrap',
    }}>{label}</span>
  );
}

function BackBtn({ onPress }) {
  return (
    <div onClick={onPress} style={{
      position:'absolute', top:55, left:14, zIndex:30,
      width:34, height:34, borderRadius:17,
      background:'rgba(255,255,255,0.95)', backdropFilter:'blur(8px)',
      boxShadow:'0 2px 8px rgba(0,0,0,0.12)',
      display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer',
    }}>
      <svg width="9" height="16" viewBox="0 0 9 16"><path d="M7.5 1.5L2 8l5.5 6.5" stroke={Z.text} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/></svg>
    </div>
  );
}

// Mini map preview
function MiniMap({ stops=3, height=130 }) {
  const pts = [[35,90],[140,30],[245,75],[330,135]].slice(0, stops);
  return (
    <svg viewBox="0 0 360 170" style={{ width:'100%', height, borderRadius:11, background:'#E8F0EE', display:'block' }}>
      <defs>
        <pattern id="grid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" stroke="#D5E3DF" strokeWidth="0.5" fill="none"/>
        </pattern>
      </defs>
      <rect width="360" height="170" fill="url(#grid)"/>
      <path d="M 0 90 Q 100 60 200 95 T 360 85" stroke="#fff" strokeWidth="13" fill="none"/>
      <path d="M 0 90 Q 100 60 200 95 T 360 85" stroke="#CCD9D5" strokeWidth="1.5" fill="none"/>
      <path d={`M ${pts.map(p=>p.join(' ')).join(' L ')}`} stroke={Z.accent} strokeWidth="2.5" strokeDasharray="5 4" fill="none"/>
      {pts.map((p, i) => (
        <g key={i}>
          <circle cx={p[0]} cy={p[1]} r="11" fill="#fff" stroke={Z.accent} strokeWidth="2.2"/>
          <text x={p[0]} y={p[1]+4} textAnchor="middle" fontSize="11" fontWeight="700" fill={Z.accent} fontFamily={SANS}>{i+1}</text>
        </g>
      ))}
    </svg>
  );
}

// ── Bottom Tab Bar ────────────────────────────────────────
function ZTabBar({ tab, onTab }) {
  const ic = a => a ? Z.primary : Z.muted;
  const items = [
    { id:'home', label:'首页' },
    { id:'scenes', label:'场景' },
    { id:'generate', label:'生成', center:true },
    { id:'assistant', label:'助手' },
    { id:'profile', label:'我的' },
  ];
  const icons = {
    home: a => <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z" stroke={ic(a)} strokeWidth="2" fill={a?Z.primary+'14':'none'}/><path d="M9 21V13h6v8" stroke={ic(a)} strokeWidth="2" strokeLinecap="round"/></svg>,
    scenes: a => <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="7" height="7" rx="1" stroke={ic(a)} strokeWidth="2" fill={a?Z.primary+'14':'none'}/><rect x="14" y="3" width="7" height="7" rx="1" stroke={ic(a)} strokeWidth="2"/><rect x="3" y="14" width="7" height="7" rx="1" stroke={ic(a)} strokeWidth="2"/><rect x="14" y="14" width="7" height="7" rx="1" stroke={ic(a)} strokeWidth="2" fill={a?Z.primary+'14':'none'}/></svg>,
    assistant: a => <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M21 12a8 8 0 01-12.5 6.6L3 20l1.4-5.5A8 8 0 1121 12z" stroke={ic(a)} strokeWidth="2" fill={a?Z.primary+'14':'none'} strokeLinejoin="round"/><circle cx="8.5" cy="12" r="1.2" fill={ic(a)}/><circle cx="12" cy="12" r="1.2" fill={ic(a)}/><circle cx="15.5" cy="12" r="1.2" fill={ic(a)}/></svg>,
    profile: a => <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke={ic(a)} strokeWidth="2" fill={a?Z.primary+'14':'none'}/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke={ic(a)} strokeWidth="2" strokeLinecap="round"/></svg>,
  };
  return (
    <div style={{
      background:'rgba(255,255,255,0.98)', backdropFilter:'blur(20px)',
      borderTop:`1px solid ${Z.border}`,
      display:'flex', alignItems:'flex-end', paddingBottom:18, paddingTop:6,
      flexShrink:0,
    }}>
      {items.map(it => (
        it.center ? (
          <div key="g" style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:3 }}>
            <div onClick={() => onTab('generate')} style={{
              width:52, height:52, borderRadius:26,
              background:`linear-gradient(135deg, ${Z.accent} 0%, #FF9558 100%)`,
              boxShadow:`0 6px 18px ${Z.accent}55`, marginTop:-14,
              display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer',
            }}>
              <svg width="24" height="24" viewBox="0 0 26 26" fill="none">
                <path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/>
              </svg>
            </div>
            <span style={{ fontSize:10, fontWeight: tab==='generate'?700:500, color: tab==='generate'?Z.accent:Z.muted }}>{it.label}</span>
          </div>
        ) : (
          <div key={it.id} onClick={() => onTab(it.id)} style={{
            flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:3, cursor:'pointer', paddingTop:2,
          }}>
            {icons[it.id](tab===it.id)}
            <span style={{ fontSize:10, fontWeight: tab===it.id?700:500, color: tab===it.id?Z.primary:Z.muted }}>{it.label}</span>
          </div>
        )
      ))}
    </div>
  );
}

// ── HOME ──────────────────────────────────────────────────
function ZHomeScreen({ navigate }) {
  return (
    <div style={{ background:Z.bg, paddingBottom:14, fontFamily:SANS }}>
      {/* Header */}
      <div style={{ background:`linear-gradient(180deg, ${Z.primary} 0%, ${Z.primary} 70%, ${Z.bg} 100%)`, padding:'55px 16px 24px' }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:14 }}>
          <div style={{ display:'flex', alignItems:'center', gap:5, cursor:'pointer' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" stroke="#fff" strokeWidth="2"/><circle cx="12" cy="9" r="3" stroke="#fff" strokeWidth="2"/></svg>
            <span style={{ color:'#fff', fontSize:14, fontWeight:700 }}>{CITY}</span>
            <svg width="9" height="9" viewBox="0 0 9 9"><path d="M1 2.5l3.5 4 3.5-4" stroke="#fff" strokeWidth="1.8" fill="none" strokeLinecap="round"/></svg>
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:5, background:'rgba(255,255,255,0.15)', borderRadius:99, padding:'4px 10px' }}>
            <span style={{ fontSize:13 }}>{WEATHER.icon}</span>
            <span style={{ color:'#fff', fontSize:12, fontWeight:600 }}>{WEATHER.temp}° {WEATHER.cond}</span>
          </div>
        </div>
        <div style={{ fontFamily:MONO, fontSize:10, color:'rgba(255,255,255,0.55)', letterSpacing:1.5 }}>ISSUE NO.05 · LOCAL FIELD GUIDE</div>
        <div style={{ fontFamily:SERIF, color:'#fff', fontSize:24, fontWeight:900, marginTop:5, letterSpacing:1 }}>今天想去哪玩？</div>
        <div style={{ color:'rgba(255,255,255,0.65)', fontSize:12, marginTop:5 }}>{WEATHER.advice} · 已为你准备 4 条本地路线</div>
      </div>

      {/* AI input (overlapping) */}
      <div style={{ margin:'-18px 14px 0', position:'relative', zIndex:2 }}>
        <div onClick={() => navigate('generate')} style={{
          background:Z.card, borderRadius:14, padding:'12px 14px',
          boxShadow:'0 8px 24px rgba(13,79,74,0.12)',
          display:'flex', alignItems:'center', gap:10, cursor:'pointer',
        }}>
          <div style={{ width:34, height:34, borderRadius:17, background:`linear-gradient(135deg,${Z.accent},#FF9558)`, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
            <svg width="17" height="17" viewBox="0 0 26 26" fill="none"><path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/></svg>
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:SERIF, fontSize:13.5, fontWeight:700, color:Z.text }}>告诉我你的想法 · AI 帮你规划</div>
            <div style={{ fontSize:10.5, color:Z.muted, marginTop:1 }}>例如：周末想去钓鱼，自驾 2 小时内</div>
          </div>
          <div style={{ background:Z.primary, borderRadius:9, padding:'5px 9px', color:'#fff', fontSize:11.5, fontWeight:700 }}>开始</div>
        </div>
      </div>

      {/* Scenes (index style) */}
      <div style={{ padding:'18px 14px 0' }}>
        <Sec no="01" title="按场景索引" sub="9 类常见出游场景"/>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:8 }}>
          {SCENES.map(s => (
            <div key={s.id} onClick={() => navigate('scenes', { sceneId: s.id })} style={{
              background:Z.card, borderRadius:11, padding:'12px 9px',
              display:'flex', flexDirection:'column', alignItems:'flex-start', gap:7, cursor:'pointer',
              boxShadow:'0 1px 4px rgba(13,79,74,0.05)',
              position:'relative',
            }}>
              <div style={{ position:'absolute', top:7, right:9, fontFamily:MONO, fontSize:9, color:Z.muted, letterSpacing:0.5 }}>{s.no}</div>
              <div style={{ width:34, height:34, borderRadius:10, background:s.color+'18', display:'flex', alignItems:'center', justifyContent:'center', fontSize:18 }}>{s.icon}</div>
              <div>
                <div style={{ fontFamily:SERIF, fontSize:12.5, fontWeight:700, color:Z.text, lineHeight:1.15 }}>{s.label}</div>
                <div style={{ fontSize:9.5, color:Z.muted, marginTop:2 }}>{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Nearby */}
      <div style={{ padding:'18px 14px 0' }}>
        <Sec no="02" title="附近现在适合去" sub="基于定位 + 天气 + 时段" action="换一批"/>
        {NEARBY.slice(0,3).map(p => (
          <div key={p.id} onClick={() => navigate('poiDetail', { poiId: p.id })} style={{
            background:Z.card, borderRadius:13, padding:11, marginBottom:9,
            boxShadow:'0 1px 6px rgba(13,79,74,0.06)',
            display:'flex', gap:11, cursor:'pointer',
          }}>
            <div style={{ width:80, height:80, borderRadius:10, overflow:'hidden', flexShrink:0, position:'relative' }}>
              <img src={p.img} alt={p.name} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
              <div style={{ position:'absolute', bottom:4, left:4, background:'rgba(0,0,0,0.55)', color:'#fff', fontSize:9, padding:'1px 5px', borderRadius:99 }}>📍 {p.dist}</div>
            </div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', gap:6 }}>
                <div>
                  <div style={{ fontFamily:MONO, fontSize:9.5, color:Z.muted, letterSpacing:0.5 }}>{p.no}</div>
                  <div style={{ fontFamily:SERIF, fontSize:14.5, fontWeight:800, color:Z.text, marginTop:1, lineHeight:1.2 }}>{p.name}</div>
                </div>
                <div style={{ fontSize:10, color:Z.muted, whiteSpace:'nowrap', marginTop:2 }}>🕐 {p.time}</div>
              </div>
              <div style={{ fontSize:10.5, color:Z.muted, marginTop:3 }}>{p.cat}</div>
              <div style={{ fontSize:11.5, color:Z.text2, marginTop:5, lineHeight:1.5, overflow:'hidden', textOverflow:'ellipsis', display:'-webkit-box', WebkitLineClamp:1, WebkitBoxOrient:'vertical' }}>💡 {p.reason}</div>
              <div style={{ display:'flex', gap:4, marginTop:6 }}>
                {p.tags.slice(0,3).map(t => <Tag key={t} label={t} color={Z.primary} small />)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Routes */}
      <div style={{ padding:'14px 14px 0' }}>
        <Sec no="03" title="精选路线" sub="人工策划 · 已审核" action="全部"/>
        <div style={{ display:'flex', gap:10, overflowX:'auto', paddingBottom:4 }}>
          {ROUTES.map(r => (
            <div key={r.id} onClick={() => navigate('result', { routeId: r.id })} style={{
              minWidth:220, flexShrink:0, background:Z.card, borderRadius:13, overflow:'hidden',
              boxShadow:'0 1px 6px rgba(13,79,74,0.06)', cursor:'pointer',
            }}>
              <div style={{ height:100, position:'relative', overflow:'hidden' }}>
                <img src={r.img} alt={r.title} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                <div style={{ position:'absolute', top:8, left:8, background:'rgba(255,255,255,0.95)', borderRadius:5, padding:'2px 7px', fontSize:10, fontWeight:700, color:r.color, fontFamily:MONO, letterSpacing:0.5 }}>{r.no}</div>
                <div style={{ position:'absolute', bottom:8, left:11, color:'#fff', fontFamily:SERIF, fontSize:14, fontWeight:800, textShadow:'0 1px 4px rgba(0,0,0,0.5)' }}>{r.title}</div>
              </div>
              <div style={{ padding:'9px 11px' }}>
                <div style={{ fontSize:11, color:Z.muted, lineHeight:1.5, marginBottom:6, height:33, overflow:'hidden', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical' }}>{r.summary}</div>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                  <span style={{ fontSize:10, color:Z.muted }}>🕐 {r.duration} · 💰 {r.budget} · 📍 {r.poi}站</span>
                  <Tag label={r.tag} color={r.color} small/>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tip banner */}
      <div style={{ margin:'14px', background:`linear-gradient(135deg, ${Z.amber}22 0%, ${Z.accent}11 100%)`, border:`1px solid ${Z.amber}44`, borderRadius:13, padding:'12px 14px', display:'flex', alignItems:'center', gap:11 }}>
        <span style={{ fontSize:22 }}>🌱</span>
        <div style={{ flex:1 }}>
          <div style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text }}>越用越准</div>
          <div style={{ fontSize:11, color:Z.muted, marginTop:1 }}>你的真实反馈让推荐更懂你</div>
        </div>
      </div>
    </div>
  );
}

// ── SCENES ────────────────────────────────────────────────
function ZScenesScreen({ navigate, initialScene='fish' }) {
  const [active, setActive] = React.useState(initialScene);
  const scene = SCENES.find(s => s.id === active) || SCENES[0];
  const isFish = active === 'fish';

  return (
    <div style={{ background:Z.bg, paddingBottom:14, fontFamily:SANS }}>
      <div style={{ background:'#fff', padding:'55px 14px 0' }}>
        <div style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:1.5 }}>§ SCENES · INDEX</div>
        <div style={{ fontFamily:SERIF, fontSize:21, fontWeight:900, color:Z.text, marginTop:4 }}>按场景索引</div>
        <div style={{ fontSize:12, color:Z.muted, marginTop:3, marginBottom:13 }}>选择场景，AI 推荐最合适的地点和路线</div>
        <div style={{ display:'flex', gap:6, overflowX:'auto', paddingBottom:11 }}>
          {SCENES.map(s => {
            const on = active === s.id;
            return (
              <div key={s.id} onClick={() => setActive(s.id)} style={{
                padding:'6px 12px', borderRadius:99,
                background: on ? s.color : Z.bg,
                color: on ? '#fff' : Z.text,
                fontSize:12, fontWeight:700, whiteSpace:'nowrap', cursor:'pointer',
                display:'flex', alignItems:'center', gap:5,
              }}>
                <span style={{ fontFamily:MONO, fontSize:9, opacity: on ? 0.85 : 0.5 }}>{s.no}</span>
                <span style={{ fontSize:13 }}>{s.icon}</span>
                {s.label}
              </div>
            );
          })}
        </div>
      </div>

      {/* Hero */}
      <div style={{ margin:'12px 14px 0', borderRadius:13, padding:'15px 16px', background:`linear-gradient(135deg, ${scene.color}, ${scene.color}DD)` }}>
        <div style={{ display:'flex', alignItems:'center', gap:11 }}>
          <div style={{ fontSize:32 }}>{scene.icon}</div>
          <div>
            <div style={{ fontFamily:MONO, fontSize:10, color:'rgba(255,255,255,0.7)', letterSpacing:1.2 }}>SCENE · {scene.no}</div>
            <div style={{ fontFamily:SERIF, color:'#fff', fontWeight:900, fontSize:19, marginTop:2 }}>{scene.label}</div>
            <div style={{ color:'rgba(255,255,255,0.85)', fontSize:12, marginTop:2 }}>{scene.desc}</div>
          </div>
        </div>
      </div>

      {/* Fish: gear */}
      {isFish && (
        <div style={{ margin:'12px 14px 0', background:Z.card, borderRadius:13, padding:'13px 14px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'baseline', marginBottom:9 }}>
            <div style={{ fontFamily:SERIF, fontSize:13.5, fontWeight:800, color:Z.text }}>🎒 装备清单</div>
            <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.5 }}>7 ITEMS</span>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'4px 14px' }}>
            {PLAN_RESULT.gearList.map(g => (
              <div key={g} style={{ display:'flex', alignItems:'center', gap:7, fontSize:11.5, color:Z.text2, padding:'4px 0' }}>
                <span style={{ width:15, height:15, borderRadius:4, border:`1.5px solid ${scene.color}`, display:'inline-flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  <svg width="9" height="9" viewBox="0 0 9 9"><path d="M1.5 4.5l2 2 4-4" stroke={scene.color} strokeWidth="1.8" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </span>
                <span>{g}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop:10, paddingTop:8, borderTop:`1px dashed ${Z.border}`, display:'flex', justifyContent:'space-between', fontSize:11, color:Z.muted }}>
            <span>⏰ 黄金时段</span>
            <span style={{ color:scene.color, fontWeight:700 }}>05:30 – 10:00 · 18:00 – 20:00</span>
          </div>
        </div>
      )}

      {/* Routes */}
      <div style={{ padding:'16px 14px 0' }}>
        <Sec no="R" title="推荐路线" sub={`${scene.label} · 已策划`}/>
        {(isFish ? [ROUTES[1]] : ROUTES.slice(0,2)).map(r => (
          <div key={r.id} onClick={() => navigate('result', { routeId: r.id })} style={{
            background:Z.card, borderRadius:13, overflow:'hidden',
            boxShadow:'0 1px 6px rgba(13,79,74,0.06)', marginBottom:10, cursor:'pointer',
          }}>
            <div style={{ height:115, position:'relative' }}>
              <img src={r.img} alt={r.title} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
              <div style={{ position:'absolute', inset:0, background:'linear-gradient(to top, rgba(13,79,74,0.72), transparent 60%)' }} />
              <div style={{ position:'absolute', top:8, left:11, background:'rgba(255,255,255,0.95)', borderRadius:5, padding:'2px 7px', fontFamily:MONO, fontSize:10, fontWeight:700, color:r.color, letterSpacing:0.5 }}>{r.no}</div>
              <div style={{ position:'absolute', bottom:9, left:11, right:11 }}>
                <div style={{ fontFamily:SERIF, color:'#fff', fontSize:15, fontWeight:800 }}>{r.title}</div>
                <div style={{ color:'rgba(255,255,255,0.85)', fontSize:11, marginTop:2 }}>🕐 {r.duration} · 💰 {r.budget} · 📍 {r.poi}站</div>
              </div>
            </div>
            <div style={{ padding:'10px 13px' }}>
              <div style={{ fontSize:12, color:Z.muted, lineHeight:1.5 }}>{r.summary}</div>
            </div>
          </div>
        ))}
      </div>

      {/* POIs */}
      <div style={{ padding:'8px 14px 0' }}>
        <Sec no="P" title="推荐地点" sub={`${scene.label} · POI`}/>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:9 }}>
          {(isFish ? [NEARBY[2]] : NEARBY).slice(0, isFish ? 1 : 4).map(p => (
            <div key={p.id} onClick={() => navigate('poiDetail', { poiId: p.id })} style={{
              background:Z.card, borderRadius:12, overflow:'hidden',
              boxShadow:'0 1px 6px rgba(13,79,74,0.06)', cursor:'pointer',
              gridColumn: isFish ? 'span 2' : 'auto',
            }}>
              <div style={{ height: isFish ? 100 : 84, position:'relative' }}>
                <img src={p.img} alt={p.name} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                <div style={{ position:'absolute', top:5, left:5, background:'rgba(0,0,0,0.6)', color:'#fff', fontFamily:MONO, fontSize:9, padding:'1.5px 5px', borderRadius:4, letterSpacing:0.5 }}>{p.no}</div>
                <div style={{ position:'absolute', top:5, right:5, background:'rgba(0,0,0,0.6)', color:'#fff', fontSize:9, padding:'1.5px 5px', borderRadius:4 }}>{p.dist}</div>
              </div>
              <div style={{ padding:'8px 10px' }}>
                <div style={{ fontFamily:SERIF, fontSize:12.5, fontWeight:700, color:Z.text }}>{p.name}</div>
                <div style={{ fontSize:10, color:Z.muted, marginTop:2 }}>🕐 {p.time} · {p.budget}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── GENERATE ──────────────────────────────────────────────
function ZGenerateScreen({ navigate }) {
  const [time, setTime] = React.useState('周六清晨');
  const [people, setPeople] = React.useState('2人');
  const [budget, setBudget] = React.useState('200元以内');
  const [transport, setTransport] = React.useState('自驾');
  const [prefs, setPrefs] = React.useState(['钓鱼','自然']);
  const [custom, setCustom] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [progress, setProgress] = React.useState(0);
  const [step, setStep] = React.useState(0);

  const steps = [
    { k:'01', t:'解析你的需求' },
    { k:'02', t:'地图 API · 查询附近 POI' },
    { k:'03', t:'知识库检索 · 路线模板匹配' },
    { k:'04', t:'WebSearch · 补充最新信息' },
    { k:'05', t:'本地 AI · 生成攻略草稿' },
    { k:'06', t:'质量校验 · 风险检查' },
  ];

  React.useEffect(() => {
    if (!loading) return;
    let p = 0;
    const iv = setInterval(() => { p += Math.random() * 10; if (p > 96) p = 96; setProgress(Math.round(p)); }, 320);
    const stepIv = setInterval(() => setStep(s => Math.min(s+1, steps.length-1)), 720);
    const done = setTimeout(() => {
      clearInterval(iv); clearInterval(stepIv); setProgress(100); setStep(steps.length-1);
      setTimeout(() => navigate('result', { generated:true }), 500);
    }, 4500);
    return () => { clearInterval(iv); clearInterval(stepIv); clearTimeout(done); };
  }, [loading]);

  const toggle = (arr, set, v) => set(arr.includes(v) ? arr.filter(x=>x!==v) : [...arr, v]);
  const Chip = ({ label, on, onPress }) => (
    <span onClick={onPress} style={{
      padding:'6px 12px', borderRadius:99,
      background: on ? Z.primary : '#fff', color: on ? '#fff' : Z.text,
      fontSize:12, fontWeight:600, cursor:'pointer',
      border: `1px solid ${on ? Z.primary : Z.border}`,
    }}>{label}</span>
  );
  const Group = ({ no, label, hint, children }) => (
    <div style={{ marginBottom:14 }}>
      <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:8 }}>
        <span style={{ fontFamily:MONO, fontSize:10, color:Z.accent, fontWeight:700, letterSpacing:0.5 }}>Q{no}</span>
        <span style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text }}>{label}</span>
        {hint && <span style={{ fontSize:10.5, color:Z.muted }}>· {hint}</span>}
      </div>
      <div style={{ display:'flex', flexWrap:'wrap', gap:7 }}>{children}</div>
    </div>
  );

  if (loading) return (
    <div style={{ background:Z.bg, height:'100%', padding:'62px 22px 20px', fontFamily:SANS, display:'flex', flexDirection:'column' }}>
      <div style={{ display:'flex', flexDirection:'column', alignItems:'center', marginBottom:28 }}>
        <div style={{
          width:84, height:84, borderRadius:42,
          background:`linear-gradient(135deg, ${Z.primary}, #2A8278)`,
          display:'flex', alignItems:'center', justifyContent:'center',
          boxShadow:`0 8px 28px ${Z.primary}33`,
          animation:'zR 3s linear infinite', marginBottom:16,
        }}>
          <svg width="38" height="38" viewBox="0 0 26 26" fill="none"><path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/></svg>
        </div>
        <div style={{ fontFamily:SERIF, fontSize:19, fontWeight:900, color:Z.text }}>规划中…</div>
        <div style={{ fontSize:11, color:Z.muted, marginTop:3, fontFamily:MONO, letterSpacing:0.5 }}>预计 {Math.max(0, Math.ceil((100-progress)/22))} 秒 · {progress}%</div>
      </div>

      <div style={{ background:Z.card, borderRadius:13, padding:'14px', boxShadow:'0 2px 10px rgba(13,79,74,0.06)' }}>
        {steps.map((s, i) => {
          const done = i < step, doing = i === step;
          return (
            <div key={i} style={{ display:'flex', alignItems:'center', gap:10, padding:'6px 0', opacity: i > step ? 0.4 : 1, transition:'all 0.3s' }}>
              <div style={{
                width:22, height:22, borderRadius:11, flexShrink:0,
                background: done ? Z.primary : (doing ? Z.accent+'22' : Z.border),
                display:'flex', alignItems:'center', justifyContent:'center',
              }}>
                {done && <svg width="10" height="10" viewBox="0 0 10 10"><path d="M2 5l2 2 4-4" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                {doing && <div style={{ width:8, height:8, borderRadius:4, background:Z.accent, animation:'zP 0.9s ease-in-out infinite' }} />}
                {!done && !doing && <span style={{ fontFamily:MONO, fontSize:9.5, color:Z.muted, fontWeight:700 }}>{s.k}</span>}
              </div>
              <span style={{ fontSize:12.5, color: doing ? Z.text : (done ? Z.text : Z.muted), fontWeight: doing ? 700 : 500 }}>{s.t}</span>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop:16, background:Z.border, borderRadius:99, height:5, overflow:'hidden' }}>
        <div style={{ width:`${progress}%`, height:5, borderRadius:99, background:`linear-gradient(90deg, ${Z.primary}, ${Z.mint})`, transition:'width 0.4s ease' }} />
      </div>

      <style>{`@keyframes zR{from{transform:rotate(0)}to{transform:rotate(360deg)}} @keyframes zP{0%,100%{transform:scale(1)}50%{transform:scale(0.5);opacity:0.5}}`}</style>
    </div>
  );

  return (
    <div style={{ background:Z.bg, paddingBottom:90, fontFamily:SANS }}>
      <div style={{ background:'#fff', padding:'55px 14px 16px' }}>
        <div style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:1.5 }}>§ GENERATE</div>
        <div style={{ fontFamily:SERIF, fontSize:21, fontWeight:900, color:Z.text, marginTop:4 }}>一键生成方案</div>
        <div style={{ fontSize:12, color:Z.muted, marginTop:3 }}>告诉我你的偏好 · AI 帮你规划可执行路线</div>
      </div>

      <div style={{ padding:'12px 14px 0' }}>
        <div style={{ background:Z.card, borderRadius:13, padding:'14px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
          <Group no="1" label="什么时间" hint="今天 / 明天 / 周末…">
            {['今天','明天','周六清晨','周日全天','晚上'].map(v => <Chip key={v} label={v} on={time===v} onPress={() => setTime(v)} />)}
          </Group>
          <Group no="2" label="和谁一起">
            {['一人','情侣','亲子','朋友','带老人','2人'].map(v => <Chip key={v} label={v} on={people===v} onPress={() => setPeople(v)} />)}
          </Group>
          <Group no="3" label="预算">
            {['免费','100元以内','200元以内','300元以内','不限'].map(v => <Chip key={v} label={v} on={budget===v} onPress={() => setBudget(v)} />)}
          </Group>
          <Group no="4" label="出行方式">
            {['步行','自驾','打车','公交/地铁'].map(v => <Chip key={v} label={v} on={transport===v} onPress={() => setTransport(v)} />)}
          </Group>
          <Group no="5" label="其他偏好" hint="可多选">
            {['室内','户外','钓鱼','自然','拍照','不太累','美食','带娃友好','安静'].map(v => <Chip key={v} label={v} on={prefs.includes(v)} onPress={() => toggle(prefs, setPrefs, v)} />)}
          </Group>
        </div>

        <div style={{ marginTop:11, background:Z.card, borderRadius:13, padding:'13px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
          <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:7 }}>
            <span style={{ fontFamily:MONO, fontSize:10, color:Z.accent, fontWeight:700, letterSpacing:0.5 }}>Q6</span>
            <span style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text }}>还想补充什么？</span>
            <span style={{ fontSize:10.5, color:Z.muted }}>· 可选 · 自然语言</span>
          </div>
          <textarea value={custom} onChange={e => setCustom(e.target.value)} placeholder="例如：希望钓点风小、人少，孩子可以玩水但要安全"
            style={{ width:'100%', minHeight:58, border:'none', resize:'none', background:Z.bg, borderRadius:9, padding:'9px 11px', fontSize:12.5, color:Z.text, outline:'none', fontFamily:SANS, boxSizing:'border-box' }} />
        </div>

        {/* Summary */}
        <div style={{ marginTop:11, background:`${Z.primary}0E`, borderLeft:`3px solid ${Z.primary}`, borderRadius:'4px 11px 11px 4px', padding:'10px 12px' }}>
          <div style={{ fontFamily:MONO, fontSize:10, color:Z.muted, marginBottom:3, letterSpacing:0.5 }}>※ 我将基于以下条件规划</div>
          <div style={{ fontSize:12, color:Z.text, lineHeight:1.65 }}>
            {time} · {people} · {budget} · {transport}
            {prefs.length > 0 && <> · <span style={{ color:Z.primary, fontWeight:700 }}>{prefs.join(' / ')}</span></>}
          </div>
        </div>

        <div onClick={() => setLoading(true)} style={{
          marginTop:14, height:50, borderRadius:13, cursor:'pointer',
          background:`linear-gradient(135deg, ${Z.accent}, #FF9558)`,
          boxShadow:`0 6px 18px ${Z.accent}44`,
          display:'flex', alignItems:'center', justifyContent:'center', gap:6,
          color:'#fff', fontFamily:SERIF, fontSize:15, fontWeight:800,
        }}>
          <svg width="17" height="17" viewBox="0 0 26 26"><path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/></svg>
          一键生成出游方案
        </div>
        <div style={{ textAlign:'center', fontSize:10.5, color:Z.muted, marginTop:8, fontFamily:MONO, letterSpacing:0.3 }}>地图 API + 知识库 + AI · 通常 3–8 秒</div>
      </div>
    </div>
  );
}

// ── RESULT ────────────────────────────────────────────────
function ZResultScreen({ navigate, generated }) {
  const p = PLAN_RESULT;
  const [saved, setSaved] = React.useState(false);
  return (
    <div style={{ background:Z.bg, paddingBottom:78, fontFamily:SANS }}>
      <div style={{ background:`linear-gradient(160deg, ${Z.primary} 0%, #163E3A 100%)`, padding:'55px 16px 22px', position:'relative' }}>
        <BackBtn onPress={() => navigate('back')} />
        <div onClick={() => setSaved(s=>!s)} style={{
          position:'absolute', top:55, right:55, width:34, height:34, borderRadius:17,
          background:'rgba(255,255,255,0.95)', boxShadow:'0 2px 8px rgba(0,0,0,0.12)',
          display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer',
        }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill={saved?Z.accent:'none'}><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2v16z" stroke={saved?Z.accent:Z.text} strokeWidth="2" strokeLinejoin="round"/></svg>
        </div>
        <div style={{ position:'absolute', top:55, right:14, width:34, height:34, borderRadius:17, background:'rgba(255,255,255,0.95)', boxShadow:'0 2px 8px rgba(0,0,0,0.12)', display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer' }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13" stroke={Z.text} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
        </div>

        <div style={{ marginTop:48 }}>
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <span style={{ fontFamily:MONO, fontSize:10, color:'rgba(255,255,255,0.6)', letterSpacing:1 }}>{p.no}</span>
            {generated && <span style={{ background:Z.accent, color:'#fff', borderRadius:4, padding:'2px 7px', fontSize:9.5, fontFamily:MONO, letterSpacing:0.5, fontWeight:700 }}>✨ AI · NEW</span>}
          </div>
          <div style={{ fontFamily:SERIF, color:'#fff', fontSize:21, fontWeight:900, marginTop:7, lineHeight:1.25 }}>{p.title}</div>
          <div style={{ color:'rgba(255,255,255,0.75)', fontSize:12, marginTop:5, lineHeight:1.6 }}>{p.summary}</div>
        </div>
        <div style={{ display:'flex', gap:6, marginTop:13 }}>
          {[['🕐', p.totalTime],['💰', p.totalBudget],['👥', p.people],[WEATHER.icon, `${WEATHER.temp}° ${WEATHER.cond}`]].map(([ic,v],i) => (
            <div key={i} style={{ flex:1, background:'rgba(255,255,255,0.12)', borderRadius:9, padding:'7px 6px', textAlign:'center' }}>
              <div style={{ fontSize:13, marginBottom:1 }}>{ic}</div>
              <div style={{ color:'#fff', fontSize:11, fontWeight:600 }}>{v}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Map */}
      <div style={{ margin:'-1px 14px 0', position:'relative' }}>
        <div style={{ background:Z.card, borderRadius:13, padding:11, boxShadow:'0 2px 10px rgba(13,79,74,0.08)' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8 }}>
            <div style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text }}>🗺 路线总览</div>
            <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.5 }}>{p.stops.length} STOPS · ~25 MIN</span>
          </div>
          <MiniMap stops={p.stops.length}/>
        </div>
      </div>

      {/* Sources */}
      <div style={{ margin:'12px 14px 0', display:'flex', flexWrap:'wrap', gap:5 }}>
        {p.sources.map(s => (
          <span key={s.t} style={{
            display:'inline-flex', alignItems:'center', gap:4,
            fontSize:10, fontFamily:SANS, padding:'3px 8px 3px 5px',
            background:Z.card, border:`1px solid ${Z.border}`, borderRadius:99,
            color:Z.text2,
          }}>
            <span style={{ background:Z.primary, color:'#fff', padding:'1px 5px', borderRadius:99, fontSize:9, fontWeight:700, letterSpacing:0.3 }}>{s.kind}</span>
            {s.t}
          </span>
        ))}
      </div>

      {/* Timeline */}
      <div style={{ padding:'14px 14px 0' }}>
        <Sec no="ITN" title="详细路线" sub="按时间顺序"/>
        {p.stops.map((st, i) => (
          <div key={i} onClick={() => navigate('poiDetail', { poiId: i+1 })} style={{ display:'flex', gap:12, position:'relative', cursor:'pointer' }}>
            <div style={{ display:'flex', flexDirection:'column', alignItems:'center', flexShrink:0 }}>
              <div style={{
                width:36, height:36, borderRadius:18,
                background: Z.accent, color:'#fff',
                display:'flex', alignItems:'center', justifyContent:'center',
                fontFamily:SERIF, fontWeight:800, fontSize:14,
                boxShadow:`0 3px 10px ${Z.accent}44`, zIndex:1,
              }}>{String(st.idx).padStart(2,'0')}</div>
              {i < p.stops.length - 1 && <div style={{ width:2, flex:1, background:`linear-gradient(180deg, ${Z.accent}99, ${Z.accent}22)`, minHeight:30, marginTop:-2 }} />}
              <div style={{ fontFamily:MONO, fontSize:10, color:Z.muted, marginTop:6 }}>{st.arrive}</div>
            </div>

            <div style={{ flex:1, paddingBottom:14, minWidth:0 }}>
              <div style={{ background:Z.card, borderRadius:13, padding:'12px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', gap:8 }}>
                  <div>
                    <div style={{ fontFamily:SERIF, fontSize:14.5, fontWeight:800, color:Z.text, lineHeight:1.2 }}>{st.name}</div>
                    <div style={{ fontSize:10.5, color:Z.muted, marginTop:2 }}>{st.cat} · {st.transport}</div>
                  </div>
                  <div style={{ fontSize:10, color:Z.muted, fontFamily:MONO, whiteSpace:'nowrap', marginTop:2 }}>停留 {st.stay}</div>
                </div>
                <div style={{ background:Z.primary+'0A', borderRadius:8, padding:'7px 10px', marginTop:8 }}>
                  <div style={{ fontFamily:MONO, fontSize:9.5, color:Z.primary, fontWeight:700, marginBottom:1, letterSpacing:0.5 }}>💡 WHY HERE</div>
                  <div style={{ fontSize:11.5, color:Z.text, lineHeight:1.55 }}>{st.reason}</div>
                </div>
                <div style={{ background:Z.amber+'12', borderRadius:8, padding:'7px 10px', marginTop:6 }}>
                  <div style={{ fontFamily:MONO, fontSize:9.5, color:'#A06700', fontWeight:700, marginBottom:1, letterSpacing:0.5 }}>⚠️ HEADS UP</div>
                  <div style={{ fontSize:11.5, color:Z.text, lineHeight:1.55 }}>{st.tip}</div>
                </div>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginTop:8, paddingTop:7, borderTop:`1px dashed ${Z.border}` }}>
                  <span style={{ fontSize:10.5, color:Z.muted }}>预算 <span style={{ color:Z.accent, fontWeight:700 }}>{st.budget}</span></span>
                  <span style={{ display:'flex', alignItems:'center', gap:4, fontSize:11, color:Z.primary, fontWeight:700 }}>
                    导航 →
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ margin:'2px 14px 0', background:Z.card, borderRadius:13, padding:'13px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
        <div style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text, marginBottom:5 }}>🔄 备用方案</div>
        <div style={{ fontSize:12, color:Z.text2, lineHeight:1.65 }}>{p.backup}</div>
      </div>

      <div style={{ margin:'9px 14px 0', padding:'9px 12px', background:Z.bg, borderRadius:9, border:`1px dashed ${Z.border}` }}>
        <div style={{ fontSize:11, color:Z.muted, lineHeight:1.6 }}>ℹ️ {p.disclaimer}</div>
      </div>

      <div style={{ position:'sticky', bottom:0, background:'rgba(255,255,255,0.97)', backdropFilter:'blur(15px)', padding:'10px 14px', borderTop:`1px solid ${Z.border}`, display:'flex', gap:8, marginTop:14 }}>
        <div style={{ flex:1, height:44, borderRadius:11, border:`1.5px solid ${Z.border}`, display:'flex', alignItems:'center', justifyContent:'center', gap:5, fontSize:12, fontWeight:700, color:Z.text, cursor:'pointer' }}>
          👍 有用
        </div>
        <div style={{ flex:1, height:44, borderRadius:11, border:`1.5px solid ${Z.border}`, display:'flex', alignItems:'center', justifyContent:'center', gap:5, fontSize:12, fontWeight:700, color:Z.text, cursor:'pointer' }}>
          💬 反馈
        </div>
        <div style={{ flex:2, height:44, borderRadius:11, display:'flex', alignItems:'center', justifyContent:'center', gap:6, background:`linear-gradient(135deg, ${Z.primary}, #2A8278)`, color:'#fff', fontFamily:SERIF, fontSize:13, fontWeight:700, cursor:'pointer', boxShadow:`0 3px 10px ${Z.primary}33` }}>
          🧭 开始出发
        </div>
      </div>
    </div>
  );
}

// ── POI DETAIL ────────────────────────────────────────────
function ZPoiDetailScreen({ navigate, poiId=1 }) {
  const p = NEARBY.find(x => x.id === poiId) || NEARBY[0];
  const [saved, setSaved] = React.useState(false);
  const isFish = p.tags.includes('钓鱼');

  return (
    <div style={{ background:Z.bg, paddingBottom:78, fontFamily:SANS }}>
      <div style={{ height:230, position:'relative', overflow:'hidden' }}>
        <img src={p.img} alt={p.name} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
        <div style={{ position:'absolute', inset:0, background:'linear-gradient(to top, rgba(13,79,74,0.6) 0%, transparent 45%)' }} />
        <BackBtn onPress={() => navigate('back')} />
        <div onClick={() => setSaved(s=>!s)} style={{ position:'absolute', top:55, right:14, width:34, height:34, borderRadius:17, background:'rgba(255,255,255,0.95)', boxShadow:'0 2px 8px rgba(0,0,0,0.12)', display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer' }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill={saved?Z.accent:'none'}><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2v16z" stroke={saved?Z.accent:Z.text} strokeWidth="2" strokeLinejoin="round"/></svg>
        </div>
      </div>

      <div style={{ margin:'-32px 14px 0', position:'relative', background:Z.card, borderRadius:13, padding:'14px', boxShadow:'0 4px 14px rgba(13,79,74,0.1)' }}>
        <div style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.8 }}>{p.no}</div>
        <div style={{ fontFamily:SERIF, fontSize:19, fontWeight:900, color:Z.text, marginTop:2 }}>{p.name}</div>
        <div style={{ fontSize:12, color:Z.muted, marginTop:3 }}>{p.cat} · 距你 {p.dist}</div>
        <div style={{ display:'flex', gap:5, marginTop:9, flexWrap:'wrap' }}>
          {p.tags.map(t => <Tag key={t} label={t} color={Z.primary} small />)}
        </div>
        <div style={{ display:'flex', marginTop:13, background:Z.bg, borderRadius:9, padding:'10px 0' }}>
          {[['推荐时长',p.time],['预算',p.budget],['距离',p.dist]].map(([k,v],i) => (
            <div key={k} style={{ flex:1, textAlign:'center', borderRight: i<2 ? `1px solid ${Z.border}` : 'none' }}>
              <div style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.primary }}>{v}</div>
              <div style={{ fontSize:10, color:Z.muted, marginTop:1 }}>{k}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ margin:'12px 14px 0', background:Z.card, borderRadius:13, padding:'13px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
        <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:7 }}>
          <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.5 }}>§ 01</span>
          <span style={{ fontFamily:SERIF, fontSize:13.5, fontWeight:800, color:Z.text }}>💡 推荐理由</span>
        </div>
        <div style={{ fontSize:12, color:Z.text, lineHeight:1.7 }}>
          {p.reason}。{isFish ? '南岸日影、风向、水温综合最佳；建议提前查询限钓公告。' : '展品丰富，特别适合带孩子参观，了解新疆历史文化。'}
        </div>
      </div>

      <div style={{ margin:'10px 14px 0', background:Z.card, borderRadius:13, padding:'13px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
        <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:9 }}>
          <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.5 }}>§ 02</span>
          <span style={{ fontFamily:SERIF, fontSize:13.5, fontWeight:800, color:Z.text }}>{isFish ? '🐟 钓况' : '👥 适合人群与场景'}</span>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:7 }}>
          {(isFish ? [
            ['鱼种','鲫鱼·鲤鱼·草鱼'],
            ['时段','05:30–10:00 黄金'],
            ['水况','水位稳定 · 14°'],
            ['风向','东北 2 级 · 适宜'],
          ] : [
            ['人群','亲子、学生、外地游客'],
            ['天气','晴天、雨天均适宜'],
            ['时段','上午、下午'],
            ['强度','轻松，无需徒步'],
          ]).map(([k,v]) => (
            <div key={k} style={{ background:Z.bg, borderRadius:8, padding:'8px 10px' }}>
              <div style={{ fontSize:10, color:Z.muted, marginBottom:2 }}>{k}</div>
              <div style={{ fontSize:12, color:Z.text, fontWeight:700 }}>{v}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ margin:'10px 14px 0', background:Z.amber+'12', border:`1px solid ${Z.amber}40`, borderRadius:13, padding:'13px' }}>
        <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:7 }}>
          <span style={{ fontFamily:MONO, fontSize:10, color:'#A06700', letterSpacing:0.5, fontWeight:700 }}>§ 03</span>
          <span style={{ fontFamily:SERIF, fontSize:13.5, fontWeight:800, color:'#A06700' }}>⚠️ 避坑提醒</span>
        </div>
        {(isFish ? [
          '水库周边手机信号弱，建议下载离线地图',
          '清晨气温较低，请带保暖外套',
          '禁止垂钓商业鱼塘区域 · 留意标识',
          '垃圾必须带走 · 严禁明火炊事',
        ] : [
          '节假日人多，建议工作日或上午前往',
          '需提前在官方公众号预约',
          '停车场车位有限，建议公共交通',
          '馆内禁止饮食',
        ]).map((t,i) => (
          <div key={i} style={{ display:'flex', gap:7, fontSize:11.5, color:Z.text, lineHeight:1.65, padding:'2px 0' }}>
            <span style={{ fontFamily:MONO, fontSize:10, color:'#A06700', fontWeight:700, flexShrink:0, marginTop:2 }}>{String(i+1).padStart(2,'0')}</span>
            <span>{t}</span>
          </div>
        ))}
      </div>

      <div style={{ margin:'10px 14px 0', background:Z.card, borderRadius:13, padding:'13px', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
        <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:9 }}>
          <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.5 }}>§ 04</span>
          <span style={{ fontFamily:SERIF, fontSize:13.5, fontWeight:800, color:Z.text }}>🗺 搭配路线</span>
        </div>
        {isFish ? (
          <div>
            {[
              ['05:30 · 出发', '从市区自驾'],
              ['07:00 · 抵达', '柴窝堡水库 · 下竿'],
              ['11:30 · 休整', '岸边野餐区'],
              ['14:00 · 返程', '途经达坂城风电场'],
            ].map(([when, what], i, arr) => (
              <div key={i} style={{ display:'flex', gap:11, padding:'5px 0', borderBottom: i < arr.length-1 ? `1px dashed ${Z.border}` : 'none' }}>
                <span style={{ fontFamily:MONO, fontSize:11, color:Z.accent, fontWeight:700, width:95, flexShrink:0 }}>{when}</span>
                <span style={{ fontSize:12, color:Z.text, fontWeight:600 }}>{what}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ display:'flex', flexWrap:'wrap', gap:6, alignItems:'center', fontSize:12, color:Z.text, lineHeight:1.8 }}>
            <span style={{ background:Z.primary, color:'#fff', borderRadius:5, padding:'2px 7px', fontWeight:600, fontSize:11 }}>上午</span>
            <span style={{ fontWeight:700 }}>{p.name}</span>
            <span style={{ color:Z.muted }}>→</span>
            <span style={{ background:Z.accent, color:'#fff', borderRadius:5, padding:'2px 7px', fontWeight:600, fontSize:11 }}>中午</span>
            <span style={{ fontWeight:700 }}>附近本地餐饮</span>
            <span style={{ color:Z.muted }}>→</span>
            <span style={{ background:Z.mint, color:'#fff', borderRadius:5, padding:'2px 7px', fontWeight:600, fontSize:11 }}>下午</span>
            <span style={{ fontWeight:700 }}>水磨沟公园</span>
          </div>
        )}
      </div>

      <div style={{ margin:'10px 14px 0', padding:'9px 12px', background:Z.bg, borderRadius:9, border:`1px dashed ${Z.border}` }}>
        <div style={{ fontSize:11, color:Z.muted, lineHeight:1.6 }}>ℹ️ 营业、水位、限钓信息以官方/管理处实时通告为准</div>
      </div>

      <div style={{ position:'sticky', bottom:0, background:'rgba(255,255,255,0.97)', backdropFilter:'blur(15px)', padding:'10px 14px', borderTop:`1px solid ${Z.border}`, display:'flex', gap:8, marginTop:14 }}>
        <div style={{ flex:1, height:44, borderRadius:11, border:`1.5px solid ${Z.primary}`, color:Z.primary, display:'flex', alignItems:'center', justifyContent:'center', gap:5, fontSize:13, fontWeight:700, cursor:'pointer' }}>
          💬 问助手
        </div>
        <div style={{ flex:2, height:44, borderRadius:11, background:`linear-gradient(135deg, ${Z.primary}, #2A8278)`, color:'#fff', display:'flex', alignItems:'center', justifyContent:'center', gap:5, fontFamily:SERIF, fontSize:13, fontWeight:800, cursor:'pointer', boxShadow:`0 3px 10px ${Z.primary}33` }}>
          🧭 地图导航前往
        </div>
      </div>
    </div>
  );
}

// ── ASSISTANT ─────────────────────────────────────────────
function ZAssistantScreen({ navigate }) {
  const [msgs, setMsgs] = React.useState(CHAT_HISTORY);
  const [input, setInput] = React.useState('');
  const [typing, setTyping] = React.useState(false);

  const send = (text) => {
    if (!text.trim()) return;
    setMsgs(m => [...m, { role:'user', text }]);
    setInput(''); setTyping(true);
    setTimeout(() => {
      setTyping(false);
      setMsgs(m => [...m, {
        role:'bot',
        text: text.includes('钓') ? '柴窝堡水库本周末适合垂钓，建议清晨前往。详见钓鱼路线 R-02。' :
              text.includes('门票') ? '该地点免费开放，无需购票。' :
              text.includes('停车') ? '附近有 3 个停车场，节假日车位紧张。' :
              '我推荐试试以下方案。详细路线可点击「生成」获取完整规划。',
        sources:[{k:'知识库', v:'已审核'}]
      }]);
    }, 1300);
  };

  const Bubble = ({ m }) => {
    if (m.chips) return (
      <div style={{ display:'flex', flexWrap:'wrap', gap:6, marginLeft:38, marginBottom:10 }}>
        {m.chips.map(c => (
          <span key={c} onClick={() => send(c)} style={{
            padding:'5px 11px', borderRadius:99, background:'#fff', border:`1px solid ${Z.primary}44`,
            color:Z.primary, fontSize:11.5, fontWeight:600, cursor:'pointer',
          }}>{c}</span>
        ))}
      </div>
    );
    if (m.role === 'user') return (
      <div style={{ display:'flex', justifyContent:'flex-end', marginBottom:11 }}>
        <div style={{
          maxWidth:'78%', background:Z.primary, color:'#fff',
          borderRadius:'14px 14px 4px 14px', padding:'9px 13px', fontSize:13, lineHeight:1.55,
        }}>{m.text}</div>
      </div>
    );
    return (
      <div style={{ display:'flex', gap:8, marginBottom:11 }}>
        <div style={{ width:30, height:30, borderRadius:15, background:`linear-gradient(135deg,${Z.primary},#2A8278)`, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, fontSize:14 }}>🤖</div>
        <div style={{ maxWidth:'78%' }}>
          <div style={{ background:'#fff', borderRadius:'14px 14px 14px 4px', padding:'10px 13px', fontSize:13, color:Z.text, lineHeight:1.65, boxShadow:'0 1px 4px rgba(13,79,74,0.06)', whiteSpace:'pre-wrap' }}>
            {m.text.split('**').map((part, i) => i % 2 === 1 ? <strong key={i} style={{ color:Z.primary }}>{part}</strong> : part)}
          </div>
          {m.sources && (
            <div style={{ display:'flex', gap:5, marginTop:6, marginLeft:2, flexWrap:'wrap' }}>
              {m.sources.map(s => (
                <span key={s.v} style={{
                  display:'inline-flex', alignItems:'center', gap:4,
                  fontSize:9.5, padding:'2px 7px 2px 4px', color:Z.muted,
                  background:Z.bg, borderRadius:99, border:`1px solid ${Z.border}`,
                }}>
                  <span style={{ background:Z.primary, color:'#fff', padding:'1px 5px', borderRadius:99, fontSize:9, fontWeight:700 }}>{s.k}</span>
                  {s.v}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ background:Z.bg, height:'100%', display:'flex', flexDirection:'column', fontFamily:SANS }}>
      <div style={{ background:'#fff', padding:'55px 14px 12px', borderBottom:`1px solid ${Z.border}` }}>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <div style={{ width:38, height:38, borderRadius:19, background:`linear-gradient(135deg,${Z.primary},#2A8278)`, display:'flex', alignItems:'center', justifyContent:'center', fontSize:18, position:'relative' }}>
            🤖
            <div style={{ position:'absolute', bottom:1, right:1, width:9, height:9, borderRadius:5, background:'#22C55E', border:'2px solid #fff' }} />
          </div>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:SERIF, fontSize:15, fontWeight:800, color:Z.text }}>出游助手</div>
            <div style={{ fontSize:10.5, color:Z.muted, fontFamily:MONO, letterSpacing:0.5 }}>本地知识库 · 在线</div>
          </div>
          <div style={{ width:32, height:32, borderRadius:16, background:Z.bg, display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 5v.01M12 12v.01M12 19v.01" stroke={Z.muted} strokeWidth="2.5" strokeLinecap="round"/></svg>
          </div>
        </div>
      </div>

      <div style={{ flex:1, overflowY:'auto', padding:'14px 12px 0' }}>
        {msgs.map((m, i) => <Bubble key={i} m={m} />)}
        {typing && (
          <div style={{ display:'flex', gap:8, marginBottom:11 }}>
            <div style={{ width:30, height:30, borderRadius:15, background:`linear-gradient(135deg,${Z.primary},#2A8278)`, display:'flex', alignItems:'center', justifyContent:'center', fontSize:14 }}>🤖</div>
            <div style={{ background:'#fff', borderRadius:'14px 14px 14px 4px', padding:'12px 14px', boxShadow:'0 1px 4px rgba(13,79,74,0.06)', display:'flex', gap:4 }}>
              {[0,1,2].map(i => <div key={i} style={{ width:6, height:6, borderRadius:3, background:Z.muted, animation:`zD 1.2s ease-in-out infinite`, animationDelay:`${i*0.2}s` }} />)}
            </div>
          </div>
        )}
      </div>

      <div style={{ padding:'4px 12px 8px', display:'flex', gap:6, overflowX:'auto' }}>
        {FAQ_QUICK.slice(2).map(q => (
          <span key={q} onClick={() => send(q)} style={{ background:'#fff', border:`1px solid ${Z.border}`, padding:'5px 10px', borderRadius:99, fontSize:11, color:Z.text, whiteSpace:'nowrap', cursor:'pointer' }}>{q}</span>
        ))}
      </div>

      <div style={{ padding:'8px 12px 14px', background:'#fff', borderTop:`1px solid ${Z.border}` }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, background:Z.bg, borderRadius:22, padding:'5px 5px 5px 14px' }}>
          <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key==='Enter' && send(input)} placeholder="问我任何出游问题…"
            style={{ flex:1, background:'transparent', border:'none', outline:'none', fontSize:13, color:Z.text, fontFamily:SANS, minWidth:0 }} />
          <div onClick={() => send(input)} style={{ width:34, height:34, borderRadius:17, background: input.trim() ? Z.primary : Z.border, display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer' }}>
            <svg width="15" height="15" viewBox="0 0 24 24"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="#fff" strokeWidth="2" fill="none" strokeLinejoin="round"/></svg>
          </div>
        </div>
      </div>

      <style>{`@keyframes zD{0%,80%,100%{opacity:0.3;transform:translateY(0)}40%{opacity:1;transform:translateY(-3px)}}`}</style>
    </div>
  );
}

// ── PROFILE ───────────────────────────────────────────────
function ZProfileScreen({ navigate }) {
  const menus1 = [
    {no:'01', icon:'🔖', label:'我的收藏', sub:'5 地点 · 2 路线'},
    {no:'02', icon:'📜', label:'出游历史', sub:'已规划 8 次出游'},
    {no:'03', icon:'✍️', label:'我的反馈', sub:'感谢你帮我们变得更好'},
    {no:'04', icon:'📍', label:'我的足迹', sub:'去过 12 个地方'},
  ];
  const menus2 = [
    {icon:'🏙', label:'当前城市', detail:CITY},
    {icon:'🔔', label:'消息通知'},
    {icon:'🛡', label:'隐私设置'},
    {icon:'ℹ️', label:'关于周密出游', detail:'v1.0'},
  ];

  const Item = ({ m, last }) => (
    <div style={{ display:'flex', alignItems:'center', gap:11, padding:'12px 14px', borderBottom: last ? 'none' : `1px solid ${Z.border}`, cursor:'pointer' }}>
      {m.no && <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, width:22, fontWeight:700 }}>{m.no}</span>}
      <span style={{ fontSize:18, width:24, textAlign:'center' }}>{m.icon}</span>
      <div style={{ flex:1 }}>
        <div style={{ fontFamily:SERIF, fontSize:13.5, fontWeight:700, color:Z.text }}>{m.label}</div>
        {m.sub && <div style={{ fontSize:10.5, color:Z.muted, marginTop:1 }}>{m.sub}</div>}
      </div>
      {m.detail && <span style={{ fontSize:11, color:Z.muted, marginRight:5 }}>{m.detail}</span>}
      <svg width="6" height="10" viewBox="0 0 7 12"><path d="M1 1l5 5-5 5" stroke={Z.muted} strokeWidth="1.8" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
    </div>
  );

  return (
    <div style={{ background:Z.bg, paddingBottom:14, fontFamily:SANS }}>
      <div style={{ background:`linear-gradient(160deg, ${Z.primary} 0%, #163E3A 100%)`, padding:'55px 16px 50px' }}>
        <div style={{ display:'flex', alignItems:'center', gap:13 }}>
          <div style={{ width:62, height:62, borderRadius:31, background:`linear-gradient(135deg,${Z.accent},#FF9558)`, display:'flex', alignItems:'center', justifyContent:'center', border:'3px solid rgba(255,255,255,0.25)' }}>
            <span style={{ fontSize:26 }}>🧭</span>
          </div>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:MONO, fontSize:10, color:'rgba(255,255,255,0.55)', letterSpacing:1.5 }}>EXPLORER · LV.2</div>
            <div style={{ fontFamily:SERIF, color:'#fff', fontSize:17, fontWeight:800, marginTop:2 }}>出游探索家</div>
            <div style={{ color:'rgba(255,255,255,0.55)', fontSize:11, marginTop:2 }}>已探索 12 个地方</div>
          </div>
        </div>
      </div>

      <div style={{ margin:'-32px 14px 0', display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:8 }}>
        {[{n:'8',l:'已生成方案',c:Z.primary},{n:'5',l:'已收藏',c:Z.accent},{n:'12',l:'足迹地点',c:Z.mint}].map(s => (
          <div key={s.l} style={{ background:Z.card, borderRadius:12, padding:'13px 0', textAlign:'center', boxShadow:'0 2px 8px rgba(13,79,74,0.08)' }}>
            <div style={{ fontFamily:SERIF, fontSize:22, fontWeight:900, color:s.c }}>{s.n}</div>
            <div style={{ fontSize:11, color:Z.muted, marginTop:2 }}>{s.l}</div>
          </div>
        ))}
      </div>

      <div style={{ margin:'12px 14px 0', background:`linear-gradient(135deg, ${Z.amber}22, ${Z.accent}10)`, border:`1px solid ${Z.amber}40`, borderRadius:13, padding:'13px 14px', display:'flex', alignItems:'center', gap:11 }}>
        <span style={{ fontSize:26 }}>🌱</span>
        <div style={{ flex:1 }}>
          <div style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text }}>你已贡献 3 条反馈</div>
          <div style={{ fontSize:11, color:Z.muted, marginTop:1 }}>每一次真实体验都在让推荐更准</div>
        </div>
        <div style={{ background:Z.accent, color:'#fff', borderRadius:99, padding:'4px 11px', fontSize:11, fontWeight:700, cursor:'pointer' }}>查看 ›</div>
      </div>

      <div style={{ margin:'14px 14px 0' }}>
        <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:7 }}>
          <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.5 }}>§ M1</span>
          <span style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text }}>我的内容</span>
        </div>
        <div style={{ background:Z.card, borderRadius:13, overflow:'hidden', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
          {menus1.map((m,i) => <Item key={m.label} m={m} last={i===menus1.length-1} />)}
        </div>
      </div>

      <div style={{ margin:'12px 14px 0' }}>
        <div style={{ display:'flex', alignItems:'baseline', gap:7, marginBottom:7 }}>
          <span style={{ fontFamily:MONO, fontSize:10, color:Z.muted, letterSpacing:0.5 }}>§ M2</span>
          <span style={{ fontFamily:SERIF, fontSize:13, fontWeight:800, color:Z.text }}>设置</span>
        </div>
        <div style={{ background:Z.card, borderRadius:13, overflow:'hidden', boxShadow:'0 1px 6px rgba(13,79,74,0.05)' }}>
          {menus2.map((m,i) => <Item key={m.label} m={m} last={i===menus2.length-1} />)}
        </div>
      </div>

      <div style={{ textAlign:'center', marginTop:18, fontSize:10, color:Z.muted, fontFamily:MONO, letterSpacing:0.5 }}>
        <div>地图 API · Dify · 本地 AI · WebSearch</div>
        <div style={{ marginTop:3, fontFamily:SERIF, fontSize:11, fontWeight:700 }}>※ 周密出游 · 让每一次出游都更稳 ※</div>
      </div>
    </div>
  );
}

Object.assign(window, {
  Z, SERIF, SANS, MONO,
  ZTabBar, BackBtn, MiniMap, Tag, Sec,
  ZHomeScreen, ZScenesScreen, ZGenerateScreen,
  ZResultScreen, ZPoiDetailScreen, ZAssistantScreen, ZProfileScreen,
  CITY, WEATHER, SCENES, NEARBY, ROUTES, PLAN_RESULT, FAQ_QUICK,
});
