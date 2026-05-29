// chuyou-screens.jsx — 12 screens for 出游助手 app
// Tokens & helpers from chuyou-tokens.jsx (window-globals)

// ════════════════════════════════════════════════════════
// 1. SPLASH SCREEN — 出游助手 / 发现身边好去处
// ════════════════════════════════════════════════════════
function ScreenSplash() {
  // Use the original reference image, with its embedded status bar cropped off,
  // and render our own CYStatusBar at the top so it sits inside the iPhone safe area.
  return (
    <Phone bg="#fff">
      <CYStatusBar />
      <div style={{ flex:1, overflow:'hidden', position:'relative', background:'#fff' }}>
        <img
          src="assets/splash-cropped.png"
          alt="出游助手 启动页"
          style={{
            width:'100%', height:'100%',
            objectFit:'cover', objectPosition:'center top',
            display:'block',
          }}
        />
      </div>
    </Phone>
  );
}

function SplashMapArt() {
  return (
    <svg viewBox="0 0 300 270" width="100%" height="100%">
      <defs>
        <linearGradient id="grass" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#A8DCAE"/>
          <stop offset="100%" stopColor="#6BBE73"/>
        </linearGradient>
        <linearGradient id="lake" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#A8D4F0"/>
          <stop offset="100%" stopColor="#6FAEDB"/>
        </linearGradient>
      </defs>
      {/* faint city silhouette */}
      <g opacity="0.18" fill="#A8D5B5">
        <rect x="10" y="40" width="22" height="80"/>
        <rect x="36" y="55" width="14" height="65"/>
        <rect x="54" y="30" width="20" height="90"/>
        <rect x="78" y="50" width="14" height="70"/>
        <rect x="210" y="35" width="22" height="85"/>
        <rect x="236" y="55" width="18" height="65"/>
        <rect x="258" y="25" width="22" height="95"/>
      </g>
      {/* island/grass platform */}
      <path d="M30 165 L60 130 L120 110 L180 105 L240 120 L270 150 L268 195 L240 220 L180 235 L120 235 L60 220 L30 195 Z"
            fill="url(#grass)" stroke="#5DAB69" strokeWidth="1.2"/>
      {/* path */}
      <path d="M70 175 Q120 165 145 150 Q170 135 200 145 Q230 155 250 180"
            fill="none" stroke="#F5F0D5" strokeWidth="14" strokeLinecap="round"/>
      {/* lake */}
      <ellipse cx="160" cy="190" rx="42" ry="22" fill="url(#lake)"/>
      <ellipse cx="160" cy="185" rx="30" ry="13" fill="#B8DDF2" opacity="0.5"/>
      {/* trees - clusters */}
      {[
        [55,150,18],[80,140,14],[105,135,16],[40,180,15],[70,205,18],[100,210,14],
        [200,135,18],[225,142,16],[250,165,18],[235,200,16],[210,215,14],
        [130,140,12],[185,125,14],[155,135,12],
      ].map(([x,y,r],i)=>(
        <g key={i}>
          <ellipse cx={x} cy={y+r*0.8} rx={r*0.7} ry={r*0.35} fill="rgba(0,0,0,0.08)"/>
          <circle cx={x} cy={y} r={r} fill={i%3===0?'#4FAB5D':i%3===1?'#6CC074':'#3E8D4F'}/>
          <circle cx={x-r*0.4} cy={y-r*0.2} r={r*0.55} fill={i%3===0?'#6CC074':'#85CE8A'}/>
        </g>
      ))}
      {/* center plaza w/ rock */}
      <ellipse cx="145" cy="155" rx="22" ry="11" fill="#C8E0C2" stroke="#9BCB9A" strokeWidth="1"/>
      <ellipse cx="145" cy="158" rx="6" ry="3" fill="#6B7280"/>
      {/* small rocks */}
      <ellipse cx="105" cy="210" rx="5" ry="2.5" fill="#6B7280"/>
      <ellipse cx="115" cy="213" rx="3" ry="1.5" fill="#9CA3AF"/>
      {/* location pin */}
      <g>
        <ellipse cx="145" cy="115" rx="14" ry="4" fill="rgba(0,0,0,0.12)"/>
        <path d="M145 50 C 130 50 120 62 120 75 C 120 90 145 110 145 110 C 145 110 170 90 170 75 C 170 62 160 50 145 50 Z"
              fill="#1A8870"/>
        <circle cx="145" cy="74" r="8" fill="#fff"/>
      </g>
    </svg>
  );
}

// ════════════════════════════════════════════════════════
// 2. LOCATING SCREEN — 正在定位中
// ════════════════════════════════════════════════════════
function ScreenLocating() {
  return (
    <Phone bg="#fff">
      <CYStatusBar />
      <NavBar title="出游助手" action={<SearchIcon s={22}/>} />
      <div style={{ flex:1, padding:'32px 24px 30px', display:'flex', flexDirection:'column', alignItems:'center' }}>
        {/* Radar */}
        <div style={{ width: 280, height: 280, position:'relative', marginTop: 12 }}>
          <svg viewBox="0 0 280 280" width="100%" height="100%">
            <defs>
              <radialGradient id="rad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#E8F2EC" stopOpacity="0.9"/>
                <stop offset="70%" stopColor="#F2F7F4" stopOpacity="0.6"/>
                <stop offset="100%" stopColor="#fff" stopOpacity="0"/>
              </radialGradient>
            </defs>
            <circle cx="140" cy="140" r="135" fill="none" stroke="#D5E8DD" strokeWidth="1" strokeDasharray="3 4"/>
            <circle cx="140" cy="140" r="100" fill="url(#rad)" stroke="#D5E8DD" strokeWidth="0.8"/>
            <circle cx="140" cy="140" r="70"  fill="none" stroke="#D5E8DD" strokeWidth="0.8"/>
            <circle cx="140" cy="140" r="40"  fill="none" stroke="#D5E8DD" strokeWidth="0.8"/>
            <line x1="140" y1="20"  x2="140" y2="260" stroke="#D5E8DD" strokeWidth="0.6"/>
            <line x1="20"  y1="140" x2="260" y2="140" stroke="#D5E8DD" strokeWidth="0.6"/>
            {/* dots around */}
            <circle cx="80"  cy="55"  r="5" fill="#3FA88A"/>
            <circle cx="240" cy="90"  r="4" fill="#5BB89B"/>
            <circle cx="220" cy="225" r="6" fill="#1A8870"/>
            <circle cx="70"  cy="225" r="4" fill="#5BB89B"/>
            <circle cx="155" cy="40"  r="3" fill="#7CCAB0"/>
            {/* central pin shadow */}
            <ellipse cx="140" cy="185" rx="20" ry="5" fill="#D5E8DD"/>
            <ellipse cx="140" cy="190" rx="32" ry="8" fill="#E8F2EC" opacity="0.7"/>
          </svg>
          {/* pin centered */}
          <div style={{ position:'absolute', left:'50%', top:'42%', transform:'translate(-50%,-50%)' }}>
            <svg width="56" height="72" viewBox="0 0 56 72">
              <path d="M28 2C14 2 4 13 4 27c0 17 24 38 24 38s24-21 24-38C52 13 42 2 28 2z" fill="#1A8870"/>
              <circle cx="28" cy="27" r="9" fill="#fff"/>
            </svg>
          </div>
        </div>

        <div style={{ marginTop: 8, fontSize: 32, fontWeight: 800, color: CY.text }}>正在定位中...</div>
        <div style={{ marginTop: 8, fontSize: 16, color: CY.muted }}>请允许获取位置权限</div>

        {/* Tip card */}
        <div style={{
          marginTop: 36, width: '100%',
          background: CY.greenLS, borderRadius: 16, padding: '18px 18px 20px',
        }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom: 10 }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M9 20h6M10 17h4M12 3a7 7 0 014 12.7c-.6.5-1 1.2-1 2V17H9v-.3c0-.8-.4-1.5-1-2A7 7 0 0112 3z"
                stroke={CY.green} strokeWidth="2" strokeLinejoin="round" fill={CY.greenL}/>
            </svg>
            <span style={{ fontSize: 17, fontWeight: 800, color: CY.green }}>定位提示</span>
          </div>
          {['开启定位权限','可获取更准确的出游推荐','保护您的位置信息安全'].map(t => (
            <div key={t} style={{ display:'flex', alignItems:'center', gap:10, padding:'6px 4px', fontSize:14, color: CY.textSub }}>
              <div style={{ width:5, height:5, borderRadius:3, background: CY.green }}/>
              {t}
            </div>
          ))}
        </div>
      </div>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 3. HOME SCREEN — 出游助手主页
// ════════════════════════════════════════════════════════
function ScreenHome() {
  const entries = [
    { title:'按场所索引', sub:'景点 / 周边 / 趣游',
      icon:(
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
          <path d="M18 4c-5 0-9 4-9 9 0 7 9 17 9 17s9-10 9-17c0-5-4-9-9-9z" fill="#7CC57F"/>
          <circle cx="18" cy="13" r="4" fill="#fff"/>
          <path d="M5 30h6l-2-3-2 1-2 2zm26 0h-6l1-3 3 1 2 2z" fill="#9DD49F" opacity="0.6"/>
        </svg>) },
    { title:'附近现在适合去', sub:'短距离 / 即刻推荐',
      icon:(
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
          <rect x="6" y="11" width="22" height="20" rx="2" fill="#FBC76D"/>
          <rect x="11" y="6" width="12" height="6" rx="1.5" fill="#E8A93D"/>
          <circle cx="17" cy="20" r="2" fill="#fff"/>
          <path d="M14 24h6v3h-6z" fill="#fff"/>
        </svg>) },
    { title:'精选路线', sub:'2小时 / 半日 / 一日',
      icon:(
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
          <path d="M9 6h18a3 3 0 013 3v18a3 3 0 01-3 3H9a3 3 0 01-3-3V9a3 3 0 013-3z" fill="#F0B8A0"/>
          <path d="M13 6c0-1.7 1.3-3 3-3h4c1.7 0 3 1.3 3 3v3h-10V6z" fill="#E89B7A"/>
          <path d="M12 18l4 4 8-8" stroke="#fff" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
        </svg>) },
    { title:'直接咨询', sub:'告诉我需求',
      icon:(
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
          <path d="M4 8h28v18H14l-6 6V8z" fill="#1A8870"/>
          <circle cx="13" cy="17" r="2" fill="#fff"/>
          <circle cx="20" cy="17" r="2" fill="#fff"/>
          <circle cx="27" cy="17" r="2" fill="#fff"/>
        </svg>) },
  ];

  const nearby = [
    { name:'人民公园',     dist:'1.2km', tags:['公园','免费','亲子','下午适合'], rating:4.7, img:'https://images.unsplash.com/photo-1591030308104-9efb78d3b85b?w=300&h=200&fit=crop' },
    { name:'东郊记忆',     dist:'2.3km', tags:['文艺','拍照','#适合晚上'],     rating:4.6, img:'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=300&h=200&fit=crop' },
    { name:'望江楼公园',   dist:'1.8km', tags:['公园','#安静','#适合散步'],     rating:4.5, img:'https://images.unsplash.com/photo-1545569310-872b9b8a4be8?w=300&h=200&fit=crop' },
  ];
  const routes = [
    { name:'2小时轻松路线', sub:'公园 · 商圈 · 拍照', dist:'约3.2km', tone:'green',
      img:'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=400&h=300&fit=crop' },
    { name:'半日文艺路线',   sub:'文艺 · 美食 · 拍照', dist:'约9.3km', tone:'warm',
      img:'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop' },
    { name:'一日畅玩路线',   sub:'自然 · 文化 · 休闲', dist:'约21km', tone:'mountain',
      img:'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop' },
  ];

  return (
    <Phone bg={CY.bg}>
      <CYStatusBar />
      {/* Header */}
      <div style={{ padding:'8px 18px 14px', background:'#fff', flexShrink:0 }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
          <div>
            <div style={{ fontSize: 24, fontWeight: 800, color: CY.green, marginBottom: 8 }}>出游助手</div>
            <div style={{ display:'flex', alignItems:'center', gap: 6, color: CY.text, fontSize: 14, fontWeight: 500 }}>
              <Pin s={16}/> <span>成都市 · 春熙路附近</span>
            </div>
          </div>
          <div style={{ paddingTop: 6, textAlign:'right' }}>
            <SearchIcon s={22}/>
            <div style={{ marginTop: 10, fontSize: 14, color: CY.text, display:'flex', alignItems:'center', gap:6, justifyContent:'flex-end' }}>
              <span style={{ fontSize: 18 }}>☀️</span><span>晴 22°C</span>
            </div>
            <div style={{ marginTop: 4, fontSize: 13, color: CY.muted, display:'flex', alignItems:'center', gap:5, justifyContent:'flex-end' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="4" stroke={CY.green} strokeWidth="2"/>
                <path d="M4 21c1-4 4-6 8-6s7 2 8 6" stroke={CY.green} strokeWidth="2" strokeLinecap="round"/>
              </svg>
              3~5km推荐范围
            </div>
          </div>
        </div>
      </div>

      <div style={{ flex:1, overflowY:'auto', paddingBottom:8 }}>
        {/* Entry Card Block */}
        <div style={{ margin:'12px 14px 0', background: CY.greenLS, borderRadius: 16, padding: '14px 14px 16px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom: 10 }}>
            <RobotMascot size={50}/>
            <div>
              <div style={{ fontSize: 20, fontWeight: 800, color: CY.text }}>出游助手</div>
              <div style={{ fontSize: 13, color: CY.textSub, marginTop: 2 }}>已根据你的位置，为你准备了4种出游方式</div>
            </div>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap: 10 }}>
            {entries.map(e => (
              <div key={e.title} style={{
                background:'#fff', borderRadius: 12, padding:'12px 12px 12px 10px',
                display:'flex', alignItems:'center', gap: 8,
                boxShadow:'0 1px 3px rgba(0,0,0,0.04)',
              }}>
                <div style={{ width:40, height:40, flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center' }}>{e.icon}</div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontSize: 14, fontWeight: 800, color: CY.text, lineHeight: 1.2 }}>{e.title}</div>
                  <div style={{ fontSize: 11, color: CY.muted, marginTop: 3, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{e.sub}</div>
                </div>
                <span style={{ color: CY.muted, fontSize: 16 }}>›</span>
              </div>
            ))}
          </div>
        </div>

        {/* Nearby list */}
        <div style={{ margin:'14px 14px 0', background:'#fff', borderRadius: 16, border:`1px solid ${CY.border}`, padding:'14px 14px 6px' }}>
          <SectionTitle title="附近现在适合去" more="更多"/>
          {nearby.map((n,i)=>(
            <div key={n.name} style={{
              display:'flex', gap:12, padding:'10px 0',
              borderTop: i>0 ? `1px solid ${CY.border}` : 'none',
            }}>
              <div style={{ width:72, height:60, borderRadius:10, overflow:'hidden', flexShrink:0, background:'#eee' }}>
                <Photo src={n.img}/>
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontSize:15, fontWeight:700, color: CY.text }}>{n.name}</div>
                <div style={{ marginTop:6, display:'flex', gap:10, flexWrap:'wrap' }}>
                  {n.tags.map(t => (
                    <span key={t} style={{ fontSize:12, color: CY.green }}>{t}</span>
                  ))}
                </div>
              </div>
              <div style={{ textAlign:'right', flexShrink:0, paddingTop:2 }}>
                <div style={{ fontSize:13, color: CY.green, fontWeight:600 }}>{n.dist}</div>
                <div style={{ marginTop:8, display:'flex', alignItems:'center', gap:3, justifyContent:'flex-end' }}>
                  <Star s={13}/><span style={{ fontSize:13, color: CY.text }}>{n.rating}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Routes */}
        <div style={{ margin:'14px 14px 14px', background:'#fff', borderRadius: 16, border:`1px solid ${CY.border}`, padding:'14px 14px 14px' }}>
          <SectionTitle title="精选路线" more="更多"/>
          <div style={{ display:'flex', gap: 10, overflowX:'auto' }}>
            {routes.map(r => (
              <div key={r.name} style={{
                minWidth: 150, height: 180, flexShrink: 0,
                borderRadius: 14, position:'relative', overflow:'hidden',
                background: r.tone==='warm' ? 'linear-gradient(180deg,#F5D9B4,#E8B98A)'
                          : r.tone==='mountain' ? 'linear-gradient(180deg,#B8D8E2,#86B8C9)'
                          : 'linear-gradient(180deg,#C6E5C8,#8BC894)',
              }}>
                <div style={{ position:'absolute', inset:0, opacity:0.5 }}>
                  <Photo src={r.img}/>
                </div>
                <div style={{ position:'absolute', inset:0, background:'linear-gradient(180deg, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0) 50%)' }}/>
                <div style={{ position:'relative', padding:'12px 12px' }}>
                  <div style={{ fontSize:15, fontWeight:800, color: CY.text }}>{r.name}</div>
                  <div style={{ fontSize:11, color: CY.text, opacity:0.75, marginTop: 4 }}>{r.sub}</div>
                </div>
                <div style={{ position:'absolute', bottom: 10, left: 12, display:'flex', alignItems:'center', gap:4, fontSize:12, color: CY.greenD, fontWeight:600 }}>
                  <Pin s={12} c={CY.greenD}/> {r.dist}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <TabBar active="home"/>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 4. CATEGORY INDEX — 按场所索引
// ════════════════════════════════════════════════════════
function ScreenCategoryIndex() {
  const cats = [
    { name:'亲子游',    sub:'带娃好去处',  bg:'#DCEDE0',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><circle cx="18" cy="14" r="6" fill="#3FA46C"/><circle cx="32" cy="16" r="5" fill="#5DBC85"/><path d="M10 38c0-6 4-10 8-10s8 4 8 10v6H10v-6z" fill="#3FA46C"/><path d="M24 40c0-5 4-9 8-9s8 4 8 9v4H24v-4z" fill="#5DBC85"/></svg>) },
    { name:'情侣约会',  sub:'浪漫好去处',  bg:'#FAE2E7',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><path d="M25 42S6 30 6 17.5C6 11 11 7 16 7c3.5 0 6.5 2 9 5.5C27.5 9 30.5 7 34 7c5 0 9 4 9 10.5C43 30 25 42 25 42z" fill="#E94B6B"/></svg>) },
    { name:'雨天室内',  sub:'不怕下雨',    bg:'#E2EBF7',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><path d="M25 6C13 6 6 16 6 24h38C44 16 37 6 25 6z" fill="#3F86D6"/><path d="M25 24v8" stroke="#3F86D6" strokeWidth="3" strokeLinecap="round"/><circle cx="14" cy="38" r="2.5" fill="#5AA1E6"/><circle cx="22" cy="42" r="2.2" fill="#5AA1E6"/><circle cx="30" cy="38" r="2.5" fill="#5AA1E6"/><circle cx="38" cy="42" r="2.2" fill="#5AA1E6"/></svg>) },
    { name:'低预算',    sub:'性价比高',    bg:'#FAEED0',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><rect x="8" y="14" width="34" height="26" rx="3" fill="#F5B73C"/><rect x="18" y="8" width="14" height="8" rx="1.5" fill="#E0A028"/><text x="25" y="32" fontSize="14" fontWeight="900" fill="#fff" textAnchor="middle" fontFamily="sans-serif">¥</text></svg>) },
    { name:'夜游',      sub:'夜晚更精彩',  bg:'#E5E2EF',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><path d="M30 8c-1 1.5-1.5 3.5-1.5 5.5C28.5 21 35 27.5 42.5 27.5c2 0 4-.5 5.5-1.5C45.5 33.5 38 39 29 39 18 39 9 30 9 19S18 6 29 6c.3 0 .7 0 1 0z" fill="#6B5BB5"/><circle cx="12" cy="10" r="1.5" fill="#9C8EE0"/><circle cx="20" cy="6" r="1.2" fill="#9C8EE0"/><circle cx="38" cy="14" r="1.4" fill="#9C8EE0"/></svg>) },
    { name:'Citywalk', sub:'城市漫步',    bg:'#DCEDE0', wide:true,
      icon:(<svg width="44" height="44" viewBox="0 0 50 50"><path d="M25 4C16 4 9 11 9 20c0 12 16 26 16 26s16-14 16-26C41 11 34 4 25 4z" fill="#3FA46C"/><path d="M16 16h18M16 22h18M16 28h18M19 12v18M25 12v18M31 12v18" stroke="#fff" strokeWidth="1" opacity="0.5"/><circle cx="25" cy="20" r="5" fill="#fff"/></svg>) },
    { name:'拍照打卡',  sub:'出片圣地',    bg:'#FAE2E7',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><rect x="6" y="14" width="38" height="26" rx="3" fill="#EA5A7A"/><rect x="16" y="10" width="12" height="6" rx="1.5" fill="#D14060"/><circle cx="25" cy="27" r="7" fill="#fff"/><circle cx="25" cy="27" r="4" fill="#EA5A7A"/><path d="M38 6l1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3z" fill="#FFD0DD"/></svg>) },
    { name:'钓鱼露营',  sub:'亲近自然',    bg:'#DCEDE0',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><path d="M25 6L8 38h34L25 6z" fill="#3FA46C"/><path d="M22 38l3-12 3 12" fill="#205A38"/><path d="M38 22c-2 0-3 1.5-3 3.5 0 3 3 6 3 6s3-3 3-6c0-2-1-3.5-3-3.5z" fill="#5DBC85"/></svg>) },
    { name:'适老休闲',  sub:'轻松舒适',    bg:'#F0E8DC',
      icon:(<svg width="50" height="50" viewBox="0 0 50 50"><circle cx="22" cy="13" r="6" fill="#B89875"/><path d="M14 42c0-7 4-12 8-12s8 5 8 12" fill="#B89875"/><path d="M32 18l-2 24" stroke="#8B6F4C" strokeWidth="2" strokeLinecap="round"/><circle cx="32" cy="42" r="2" fill="#8B6F4C"/></svg>) },
  ];
  return (
    <Phone bg="#fff">
      <CYStatusBar />
      <NavBar title="按场所索引" subtitle="选择你感兴趣的类型"/>
      <div style={{ flex:1, overflowY:'auto', padding:'18px 18px 30px' }}>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap: 12 }}>
          {cats.map(c => (
            <div key={c.name} style={{
              background: c.bg, borderRadius: 14, padding:'18px 14px 16px',
              display:'flex', flexDirection:'column', alignItems:'center',
              minHeight: 130,
            }}>
              <div style={{ height: 56, display:'flex', alignItems:'center', justifyContent:'center', marginBottom: 6 }}>{c.icon}</div>
              <div style={{ fontSize: 17, fontWeight: 800, color: CY.text }}>{c.name}</div>
              <div style={{ fontSize: 12, color: CY.muted, marginTop: 4 }}>{c.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 5. CATEGORY LIST — 亲子游
// ════════════════════════════════════════════════════════
function ScreenCategoryList() {
  const filters = [
    { l:'全部',    active:true },
    { l:'公园' },
    { l:'乐园' },
    { l:'博物馆' },
    { l:'室内' },
  ];
  const places = [
    { name:'成都动物园',     desc:'动物丰富，孩子喜欢',     dist:'1.6km', rating:4.7, tags:[['动物主题','green'],['亲子','green']],
      img:'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&h=300&fit=crop'},
    { name:'欢乐谷',         desc:'游乐设施多，适合亲子',   dist:'3.2km', rating:4.6, tags:[['游乐园','green'],['亲子','green']],
      img:'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?w=400&h=300&fit=crop'},
    { name:'成都科技馆',     desc:'动脑启蒙，寓教于乐',     dist:'2.4km', rating:4.6, tags:[['科技馆','green'],['室内','blue']],
      img:'https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=300&fit=crop'},
    { name:'锦城湖公园',     desc:'大草坪，适合亲子野餐',   dist:'2.1km', rating:4.5, tags:[['亲子','green'],['免费','green']],
      img:'https://images.unsplash.com/photo-1502780402662-acc01917cf57?w=400&h=300&fit=crop'},
    { name:'海昌极地海洋公园',desc:'海洋动物丰富',           dist:'4.8km', rating:4.4, tags:[['海洋主题','green'],['亲子','green']],
      img:'https://images.unsplash.com/photo-1583244532610-2a234e9cb6b1?w=400&h=300&fit=crop'},
    { name:'乐高探索中心',   desc:'室内乐园，适合雨天',     dist:'3.1km', rating:4.5, tags:[['室内','green'],['亲子','green']],
      img:'https://images.unsplash.com/photo-1587653263995-422546a7a569?w=400&h=300&fit=crop'},
    { name:'熊猫基地亲子乐园',desc:'近距离看熊猫，亲子互动', dist:'3.6km', rating:4.6, tags:[['动物主题','green'],['亲子','green']],
      img:'https://images.unsplash.com/photo-1591128889302-c8b2c4c3b1d9?w=400&h=300&fit=crop'},
  ];
  return (
    <Phone bg="#fff">
      <CYStatusBar/>
      <NavBar title="亲子游" action={<SearchIcon s={22}/>}/>
      {/* Filters */}
      <div style={{ display:'flex', gap:10, padding:'14px 18px 12px', overflowX:'auto', flexShrink:0 }}>
        {filters.map(f => (
          <div key={f.l} style={{
            padding:'7px 18px', borderRadius: 8, fontSize: 14, fontWeight: 500,
            background: f.active ? CY.greenL : '#F4F5F6',
            color: f.active ? CY.green : CY.textSub,
            whiteSpace:'nowrap',
          }}>{f.l}</div>
        ))}
      </div>

      <div style={{ flex:1, overflowY:'auto', padding:'4px 14px 14px' }}>
        {places.map(p => (
          <div key={p.name} style={{
            background:'#fff', borderRadius: 14, border:`1px solid ${CY.border}`,
            padding: 12, marginBottom: 10, display:'flex', gap: 12,
            boxShadow:'0 1px 3px rgba(0,0,0,0.03)',
          }}>
            <div style={{ width: 90, height: 90, borderRadius: 10, overflow:'hidden', flexShrink:0, background:'#eee' }}>
              <Photo src={p.img}/>
            </div>
            <div style={{ flex:1, minWidth:0, display:'flex', flexDirection:'column' }}>
              <div style={{ display:'flex', justifyContent:'space-between', gap:8 }}>
                <div style={{ fontSize:16, fontWeight:700, color: CY.text }}>{p.name}</div>
                <div style={{ fontSize:13, color: CY.green, fontWeight:600, flexShrink:0 }}>{p.dist}</div>
              </div>
              <div style={{ fontSize:13, color: CY.muted, marginTop: 4 }}>{p.desc}</div>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-end', marginTop:'auto', paddingTop:8 }}>
                <div style={{ display:'flex', gap: 6 }}>
                  {p.tags.map(([t,c]) => <Chip key={t} label={t} color={c} size="sm"/>)}
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:3 }}>
                  <Star s={13}/><span style={{ fontSize:13, color: CY.text }}>{p.rating}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <TabBar active="discover"/>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 6. NEARBY LIST — 附近现在适合去
// ════════════════════════════════════════════════════════
function ScreenNearbyList() {
  const filters = [
    { l:'全部', active:true },
    { l:'推荐', active:true, hot:true },
    { l:'最近' },
    { l:'免费' },
    { l:'室内' },
  ];
  const items = [
    { name:'人民公园', desc:'距离近，适合下午散步',     dist:'1.2km', rating:4.7, tags:[['免费','green'],['公园','green'],['亲子','blue']],
      img:'https://images.unsplash.com/photo-1591030308104-9efb78d3b85b?w=400&h=300&fit=crop'},
    { name:'欢乐谷',   desc:'室内设施多，适合亲子',     dist:'3.2km', rating:4.6, tags:[['室内','green'],['亲子','blue'],['游乐','blue']],
      img:'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?w=400&h=300&fit=crop'},
    { name:'太古里商圈', desc:'逛街购物，美食多',         dist:'1.5km', rating:4.6, tags:[['商圈','green'],['免费','green'],['夜景','green']],
      img:'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=400&h=300&fit=crop'},
    { name:'锦江湿公园', desc:'安静，适合散步',           dist:'1.8km', rating:4.6, tags:[['免费','green'],['公园','green'],['亲子','blue']],
      img:'https://images.unsplash.com/photo-1545569310-872b9b8a4be8?w=400&h=300&fit=crop'},
    { name:'东郊记忆',   desc:'文艺打卡，适合拍照',       dist:'2.3km', rating:4.6, tags:[['文艺打卡','green'],['免费','green'],['拍照','blue']],
      img:'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=400&h=300&fit=crop'},
    { name:'环球中心',   desc:'室内游玩，适合雨天',       dist:'3.1km', rating:4.5, tags:[['免费','green'],['公园','green'],['亲子','blue']],
      img:'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop'},
  ];
  return (
    <Phone bg="#fff">
      <CYStatusBar/>
      <NavBar title="附近现在适合去" action={<SearchIcon s={22}/>}/>
      <div style={{ display:'flex', gap:10, padding:'14px 18px 12px', overflowX:'auto', flexShrink:0 }}>
        {filters.map((f,i) => (
          <div key={f.l+i} style={{
            padding:'7px 18px', borderRadius: 8, fontSize: 14, fontWeight: 500,
            background: f.active ? CY.greenL : '#F4F5F6',
            color: f.active ? CY.green : CY.textSub,
            whiteSpace:'nowrap',
          }}>{f.l}</div>
        ))}
      </div>
      <div style={{ flex:1, overflowY:'auto', padding:'4px 14px 14px' }}>
        {items.map(p => (
          <div key={p.name} style={{
            background:'#fff', borderRadius: 14, border:`1px solid ${CY.border}`,
            padding: 12, marginBottom: 10, display:'flex', gap: 12,
            boxShadow:'0 1px 3px rgba(0,0,0,0.03)',
          }}>
            <div style={{ width: 90, height: 90, borderRadius: 10, overflow:'hidden', flexShrink:0, background:'#eee' }}>
              <Photo src={p.img}/>
            </div>
            <div style={{ flex:1, minWidth:0, display:'flex', flexDirection:'column' }}>
              <div style={{ display:'flex', justifyContent:'space-between', gap:8 }}>
                <div style={{ fontSize:16, fontWeight:700, color: CY.text }}>{p.name}</div>
                <div style={{ fontSize:13, color: CY.green, fontWeight:600, flexShrink:0 }}>{p.dist}</div>
              </div>
              <div style={{ fontSize:13, color: CY.muted, marginTop: 4 }}>{p.desc}</div>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-end', marginTop:'auto', paddingTop:8 }}>
                <div style={{ display:'flex', gap: 6 }}>
                  {p.tags.map(([t,c]) => <Chip key={t} label={t} color={c} size="sm"/>)}
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:3 }}>
                  <Star s={13}/><span style={{ fontSize:13, color: CY.text }}>{p.rating}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <TabBar active="home"/>
    </Phone>
  );
}

Object.assign(window, {
  ScreenSplash, ScreenLocating, ScreenHome,
  ScreenCategoryIndex, ScreenCategoryList, ScreenNearbyList,
});
