// chuyou-screens-b.jsx — Screens 7-12 for 出游助手

// ════════════════════════════════════════════════════════
// 7. ROUTES — 精选路线 (2小时/半日/一日)
// ════════════════════════════════════════════════════════
function ScreenRoutes() {
  const tabs = [
    { l:'2小时', active:true },
    { l:'半日' },
    { l:'一日' },
  ];
  const items = [
    { name:'2小时轻松路线', spots:'公园步道 · 湖畔栈道 · 植物园 · 观景台', time:'约2小时', n:'3个地点', dist:'约3.2km',
      img:'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=600&h=400&fit=crop' },
    { name:'2小时亲子路线', spots:'动物园 · 公园 · 商场 · 商店',               time:'约2小时', n:'3个地点', dist:'约4.1km',
      img:'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=600&h=400&fit=crop' },
    { name:'2小时文艺路线', spots:'博物馆 · 文创园 · 特色咖啡馆',               time:'约2小时', n:'3个地点', dist:'约3.8km',
      img:'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=600&h=400&fit=crop' },
  ];
  return (
    <Phone bg="#fff">
      <CYStatusBar/>
      <NavBar title="精选路线" subtitle="多种时长路线组合"/>
      {/* Tabs */}
      <div style={{ display:'flex', padding:'10px 0 0', borderBottom:`1px solid ${CY.border}`, flexShrink:0 }}>
        {tabs.map(t => (
          <div key={t.l} style={{
            flex:1, textAlign:'center', padding:'14px 0 12px',
            position:'relative',
            fontSize: 18, fontWeight: t.active?800:500,
            color: t.active ? CY.greenD : CY.muted,
          }}>
            {t.l}
            {t.active && (
              <div style={{ position:'absolute', bottom:-1, left:'30%', right:'30%', height:3, background:CY.greenD, borderRadius:2 }}/>
            )}
          </div>
        ))}
      </div>
      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px 30px' }}>
        {items.map(r => (
          <div key={r.name} style={{
            background:'#fff', borderRadius: 16, border:`1px solid ${CY.border}`,
            padding: 14, marginBottom: 14, display:'flex', gap: 14,
            boxShadow:'0 2px 6px rgba(0,0,0,0.03)',
          }}>
            <div style={{ width: 110, height: 110, borderRadius: 12, overflow:'hidden', flexShrink:0 }}>
              <Photo src={r.img}/>
            </div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontSize: 17, fontWeight: 800, color: CY.text }}>{r.name}</div>
              <div style={{ fontSize: 13, color: CY.textSub, marginTop: 6, lineHeight: 1.5 }}>{r.spots}</div>
              <div style={{ display:'flex', alignItems:'center', gap: 14, marginTop: 12, fontSize: 13, color: CY.textSub }}>
                <span style={{ display:'flex', alignItems:'center', gap: 4 }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="9" stroke={CY.green} strokeWidth="2"/>
                    <path d="M12 7v5l3 2" stroke={CY.green} strokeWidth="2" strokeLinecap="round"/>
                  </svg>{r.time}
                </span>
                <span style={{ width:1, height:12, background: CY.border }}/>
                <span style={{ display:'flex', alignItems:'center', gap: 4 }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="6" r="2.5" fill={CY.green}/>
                    <path d="M9 13l3-2 3 2v8M12 11l-3 5M12 11l3 5" stroke={CY.green} strokeWidth="1.8" strokeLinecap="round" fill="none"/>
                  </svg>{r.n}
                </span>
              </div>
              <div style={{ marginTop: 10, textAlign:'right', color: CY.green, fontWeight:600, fontSize: 14 }}>{r.dist}</div>
            </div>
          </div>
        ))}
      </div>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 8. ROUTE DETAIL — 2小时轻松路线
// ════════════════════════════════════════════════════════
function ScreenRouteDetail() {
  const stops = [
    { n:1, name:'人民公园',     desc:'公园 · 休闲 · 散步，感受城市慢生活', dist:'900m' },
    { n:2, name:'太古里商圈',   desc:'逛街 · 美食 · 潮流，体验成都时尚地标', dist:'1.6km' },
    { n:3, name:'四川博物馆',   desc:'文化 · 历史 · 展览，了解巴蜀文化', dist:'700m' },
  ];
  return (
    <Phone bg="#fff">
      <CYStatusBar/>
      <NavBar title="2小时轻松路线"/>
      <div style={{ flex:1, overflowY:'auto' }}>
        {/* Tags */}
        <div style={{ padding:'14px 18px 12px', display:'flex', gap: 8, flexWrap:'wrap' }}>
          {[['轻松','green'],['亲子','green'],['适合下午','green'],['低预算','green']].map(([t,c])=>
            <Chip key={t} label={t} color={c}/>
          )}
        </div>
        <div style={{ padding:'0 18px', fontSize: 14, color: CY.textSub, lineHeight: 1.6 }}>
          公园散步，商圈逛街，博物馆参观，适合家庭和轻松出行
        </div>
        {/* Stats */}
        <div style={{ display:'flex', padding:'18px 18px', gap: 14, fontSize: 14, color: CY.textSub }}>
          <span style={{ display:'flex', alignItems:'center', gap:5 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke={CY.text} strokeWidth="2"/>
              <path d="M12 7v5l3 2" stroke={CY.text} strokeWidth="2" strokeLinecap="round"/>
            </svg>约2小时
          </span>
          <span style={{ display:'flex', alignItems:'center', gap:5 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M16 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M20 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke={CY.text} strokeWidth="2" strokeLinecap="round"/>
              <circle cx="8" cy="7" r="4" stroke={CY.text} strokeWidth="2"/>
            </svg>3个地点
          </span>
          <span style={{ display:'flex', alignItems:'center', gap:5 }}>
            <Pin s={16} c={CY.text}/>约3.2km
          </span>
        </div>

        {/* Map */}
        <div style={{ margin:'0 18px', borderRadius: 14, overflow:'hidden', height: 220, position:'relative', border:`1px solid ${CY.border}` }}>
          <RouteMap/>
        </div>

        {/* Stops */}
        <div style={{ padding:'18px 18px 8px' }}>
          <div style={{ fontSize: 17, fontWeight: 800, color: CY.text, marginBottom: 8 }}>路线地点</div>
          {stops.map((s, i) => (
            <div key={s.n} style={{
              display:'flex', gap: 14, padding: '14px 0',
              borderBottom: i < stops.length-1 ? `1px solid ${CY.border}` : 'none',
            }}>
              <div style={{
                width: 32, height: 32, borderRadius: 16, background: CY.greenD,
                color:'#fff', fontWeight: 800, fontSize: 15, flexShrink: 0,
                display:'flex', alignItems:'center', justifyContent:'center',
              }}>{s.n}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: CY.text }}>{s.name}</div>
                <div style={{ fontSize: 13, color: CY.muted, marginTop: 4 }}>{s.desc}</div>
              </div>
              <div style={{ fontSize: 13, color: CY.text, paddingTop: 6, flexShrink: 0 }}>{s.dist}</div>
            </div>
          ))}
        </div>
        <div style={{ height: 90 }}/>
      </div>

      {/* Bottom action */}
      <div style={{ padding:'12px 18px 28px', background:'#fff', flexShrink:0 }}>
        <div style={{
          background: CY.greenD, color:'#fff', height: 56, borderRadius: 30,
          display:'flex', alignItems:'center', justifyContent:'center',
          fontSize: 19, fontWeight: 800, letterSpacing: 2,
        }}>跟着路线导航</div>
      </div>
    </Phone>
  );
}

function RouteMap() {
  return (
    <svg viewBox="0 0 360 220" width="100%" height="100%" style={{ background:'#E8EFE9' }}>
      {/* river */}
      <path d="M0 50 Q60 70 100 50 T200 60 T360 50 L360 80 Q280 95 200 85 T100 80 T0 80 Z" fill="#B5D8E5"/>
      <path d="M0 50 Q60 70 100 50 T200 60 T360 50" stroke="#7BAEC2" strokeWidth="1" fill="none"/>
      {/* roads */}
      <g stroke="#fff" strokeWidth="6" fill="none">
        <path d="M30 200 L80 160 L150 145 L240 130 L330 120"/>
        <path d="M100 220 L130 180 L170 145"/>
        <path d="M220 220 L240 180 L250 145"/>
      </g>
      <g stroke="#D0D5D8" strokeWidth="1" fill="none">
        <path d="M30 200 L80 160 L150 145 L240 130 L330 120"/>
      </g>
      {/* park areas */}
      <ellipse cx="55" cy="180" rx="22" ry="14" fill="#D5E8DD"/>
      <ellipse cx="330" cy="180" rx="25" ry="16" fill="#D5E8DD"/>
      <ellipse cx="180" cy="200" rx="30" ry="12" fill="#D5E8DD"/>
      {/* tree dots */}
      {[[40,170],[70,185],[60,195],[320,170],[340,190],[170,205],[195,200],[210,210]].map(([x,y],i)=>(
        <circle key={i} cx={x} cy={y} r="3" fill="#7AB582"/>
      ))}
      {/* labels */}
      <text x="80" y="145" fontSize="11" fill="#4A5660" fontFamily="sans-serif">宽窄巷子</text>
      <text x="160" y="195" fontSize="11" fill="#4A5660" fontFamily="sans-serif">天府广场</text>
      <text x="245" y="140" fontSize="11" fill="#4A5660" fontFamily="sans-serif">春熙路</text>
      <text x="310" y="155" fontSize="11" fill="#4A5660" fontFamily="sans-serif">攒星路</text>
      <text x="340" y="80" fontSize="11" fill="#4A5660" fontFamily="sans-serif">缔江</text>
      {/* route line */}
      <path d="M75 180 L180 150 L280 130" stroke="#1A8870" strokeWidth="3.5" fill="none" strokeLinecap="round"/>
      {/* pins */}
      {[[75,180,'1','人民公园'],[180,150,'2','太古里'],[280,130,'3','四川博物馆']].map(([x,y,n,label],i)=>(
        <g key={i}>
          <path d={`M${x-12} ${y-14} a12 12 0 1 1 24 0 c0 10 -12 22 -12 22 s-12 -12 -12 -22 z`} fill="#E94B5A"/>
          <circle cx={x} cy={y-14} r="9" fill="#fff"/>
          <text x={x} y={y-10} fontSize="11" fontWeight="700" fill="#E94B5A" textAnchor="middle" fontFamily="sans-serif">{n}</text>
          <text x={x+10} y={y+22} fontSize="11" fill="#222" fontFamily="sans-serif">{label}</text>
        </g>
      ))}
    </svg>
  );
}

// ════════════════════════════════════════════════════════
// 9. PLACE DETAIL — 人民公园
// ════════════════════════════════════════════════════════
function ScreenPlaceDetail() {
  return (
    <Phone bg="#fff">
      <CYStatusBar/>
      <NavBar title="地点详情" action={
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M14 4h6v6M20 4l-8 8M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4" stroke={CY.text} strokeWidth="2" strokeLinecap="round"/>
        </svg>
      }/>
      <div style={{ flex:1, overflowY:'auto' }}>
        {/* Hero */}
        <div style={{ margin:'12px 14px 16px', height: 210, borderRadius: 16, overflow:'hidden', position:'relative', background:'#eee' }}>
          <Photo src="https://images.unsplash.com/photo-1591030308104-9efb78d3b85b?w=800&h=500&fit=crop"/>
          <div style={{
            position:'absolute', left: 12, top: 12,
            width: 32, height: 32, borderRadius: 16,
            background:'rgba(255,255,255,0.85)',
            display:'flex', alignItems:'center', justifyContent:'center',
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M15 5l-7 7 7 7" stroke={CY.text} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>

        {/* Title block */}
        <div style={{ padding:'0 18px' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
            <div style={{ fontSize: 30, fontWeight: 800, color: CY.text }}>人民公园</div>
            <div style={{ display:'flex', alignItems:'center', gap:5, paddingTop:14 }}>
              <Star s={20}/><span style={{ fontSize: 20, color: CY.text, fontWeight:600 }}>4.7</span>
              <span style={{ fontSize: 14, color: CY.muted }}>分</span>
            </div>
          </div>
          <div style={{ marginTop: 10, fontSize: 15, color: CY.green }}>
            公园　｜　免费　｜　1.2km
          </div>
          <div style={{ marginTop: 18, fontSize: 15, color: CY.text, lineHeight: 1.7 }}>
            庭院式，适合下午散步，环境优美，适合亲子和老人休闲。
          </div>
          <div style={{ marginTop: 18, display:'flex', gap: 10, flexWrap:'wrap' }}>
            {['免费','亲子','散步','下午适合'].map(t => (
              <span key={t} style={{
                padding:'6px 14px', borderRadius: 16,
                background: CY.greenL, color: CY.textSub, fontSize: 13,
              }}>{t}</span>
            ))}
          </div>
        </div>

        {/* Info rows */}
        <div style={{ margin:'24px 18px 0', borderTop:`1px solid ${CY.border}` }}>
          {[
            ['地址','成都市青羊区人民中路一段'],
            ['开放时间','全天开放'],
            ['适合人群','亲子、老人、情侣、朋友'],
            ['建议时长','1~2小时'],
          ].map(([k,v]) => (
            <div key={k} style={{
              display:'flex', padding:'16px 0', borderBottom:`1px solid ${CY.border}`,
              fontSize: 15,
            }}>
              <div style={{ width: 100, color: CY.green }}>{k}</div>
              <div style={{ flex:1, color: CY.text }}>{v}</div>
            </div>
          ))}
        </div>
        <div style={{ height: 100 }}/>
      </div>

      {/* Footer actions */}
      <div style={{
        padding:'14px 18px 26px', background:'#fff', borderTop:`1px solid ${CY.border}`,
        display:'flex', alignItems:'center', gap: 18, flexShrink:0,
      }}>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap: 2 }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.9-6.2-3.3-6.2 3.3 1.2-6.9-5-4.9 6.9-1L12 2z" stroke={CY.text} strokeWidth="1.8" strokeLinejoin="round"/>
          </svg>
          <span style={{ fontSize: 12, color: CY.text }}>收藏</span>
        </div>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap: 2 }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M14 4h6v6M20 4l-8 8M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4" stroke={CY.text} strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span style={{ fontSize: 12, color: CY.text }}>分享</span>
        </div>
        <div style={{
          flex:1, background: CY.greenD, color:'#fff', height: 50, borderRadius: 25,
          display:'flex', alignItems:'center', justifyContent:'center', gap: 8,
          fontSize: 16, fontWeight: 700,
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="#fff" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" fill="none"/>
          </svg>
          导航去这里
        </div>
      </div>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 10. CHAT EMPTY — 出游助手 咨询 (开场)
// ════════════════════════════════════════════════════════
function ScreenChatEmpty() {
  const suggestions = [
    '带孩子2小时内去哪玩?',
    '雨天室内去哪?',
    '夜晚适合去哪里?',
    '低预算去哪?',
    '附近适合约会吗?',
  ];
  return (
    <Phone bg={CY.bg}>
      <CYStatusBar/>
      <NavBar title="出游助手" action={<SearchIcon s={22}/>}/>
      <div style={{ padding:'10px 18px 0', display:'flex', alignItems:'center', gap:6 }}>
        <Pin s={16}/>
        <span style={{ fontSize: 14, color: CY.green, fontWeight: 500 }}>成都市 · 春熙路附近</span>
      </div>

      <div style={{ flex:1, padding:'20px 18px 6px', overflowY:'auto' }}>
        {/* Bot greeting */}
        <div style={{ display:'flex', alignItems:'flex-start', gap: 10 }}>
          <RobotMascot size={44}/>
          <div style={{
            background:'#F0EDE6', color: CY.text, borderRadius: 14,
            padding:'12px 14px', fontSize: 15, maxWidth: 240, lineHeight: 1.5,
          }}>
            你好呀！我是出游助手,<br/>有什么可以帮你的吗?
          </div>
        </div>

        {/* Suggestion chips */}
        <div style={{ marginTop: 18, display:'flex', flexWrap:'wrap', gap: 10 }}>
          {suggestions.map(s => (
            <div key={s} style={{
              background: CY.greenL, color: CY.text,
              padding:'10px 16px', borderRadius: 22, fontSize: 14,
            }}>{s}</div>
          ))}
        </div>
      </div>

      {/* Input */}
      <div style={{ padding:'10px 16px 24px', background: CY.bg, flexShrink:0 }}>
        <div style={{
          background:'#fff', border:`1px solid ${CY.border}`,
          borderRadius: 25, padding:'12px 16px', display:'flex', alignItems:'center', gap: 12,
        }}>
          <span style={{ flex:1, fontSize: 14, color: CY.muted }}>问问附近适合去哪...</span>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke={CY.muted} strokeWidth="1.8"/>
            <circle cx="9" cy="10" r="1" fill={CY.muted}/>
            <circle cx="15" cy="10" r="1" fill={CY.muted}/>
            <path d="M8.5 14.5c1 1.2 2.2 1.8 3.5 1.8s2.5-.6 3.5-1.8" stroke={CY.muted} strokeWidth="1.6" strokeLinecap="round"/>
          </svg>
          <div style={{
            width: 28, height: 28, borderRadius: 14, background: CY.greenL,
            display:'flex', alignItems:'center', justifyContent:'center',
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke={CY.green} strokeWidth="2.5" strokeLinecap="round"/></svg>
          </div>
        </div>
      </div>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 11. CHAT WITH REPLY — 推荐卡片
// ════════════════════════════════════════════════════════
function ScreenChatReply() {
  const cards = [
    { name:'成都动物园',   desc:'动物丰富，孩子很喜欢',   img:'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=300&h=200&fit=crop' },
    { name:'锦城湖公园',   desc:'大草坪，适合亲子活动',   img:'https://images.unsplash.com/photo-1502780402662-acc01917cf57?w=300&h=200&fit=crop' },
    { name:'欢乐谷',       desc:'游乐设施多，欢乐互动',   img:'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?w=300&h=200&fit=crop' },
  ];
  return (
    <Phone bg={CY.bg}>
      <CYStatusBar/>
      <NavBar title="出游助手" action={<SearchIcon s={22}/>}/>
      <div style={{ padding:'10px 18px 0', display:'flex', alignItems:'center', gap:6 }}>
        <Pin s={16}/>
        <span style={{ fontSize: 14, color: CY.green, fontWeight: 500 }}>成都市 · 春熙路附近</span>
      </div>

      <div style={{ flex:1, padding:'18px 18px 6px', overflowY:'auto' }}>
        {/* User msg */}
        <div style={{ display:'flex', justifyContent:'flex-end', alignItems:'flex-start', gap: 8 }}>
          <div style={{
            background: CY.greenL, color: CY.text, borderRadius: 14,
            padding:'10px 14px', fontSize: 15,
          }}>带孩子2小时内去哪玩?</div>
          <div style={{
            width: 32, height: 32, borderRadius: 16, background: '#E5E7EB',
            display:'flex', alignItems:'center', justifyContent:'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" stroke="#6B7280" strokeWidth="1.8" fill="#fff"/>
              <path d="M4 21c1-4 4-6 8-6s7 2 8 6" stroke="#6B7280" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          </div>
        </div>

        {/* Bot reply */}
        <div style={{ marginTop: 18, display:'flex', alignItems:'flex-start', gap: 10 }}>
          <RobotMascot size={44}/>
          <div style={{ flex:1 }}>
            <div style={{
              background:'#F0EDE6', color: CY.text, borderRadius: 14,
              padding:'12px 14px', fontSize: 15, lineHeight: 1.5,
            }}>
              根据你的位置，推荐这几个适合亲子游玩的地方:
            </div>
            <div style={{
              marginTop: 10, background:'#F0EDE6', borderRadius: 14, padding: 12,
              display:'flex', flexDirection:'column', gap: 10,
            }}>
              {cards.map(c => (
                <div key={c.name} style={{
                  background:'#fff', borderRadius: 12, padding: 10,
                  display:'flex', alignItems:'center', gap: 10,
                }}>
                  <div style={{ width: 62, height: 56, borderRadius: 8, overflow:'hidden', flexShrink:0, background:'#eee' }}>
                    <Photo src={c.img}/>
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: CY.text }}>{c.name}</div>
                    <div style={{ fontSize: 12, color: CY.muted, marginTop: 4 }}>{c.desc}</div>
                  </div>
                  <div style={{
                    background: CY.greenD, color:'#fff',
                    padding:'7px 14px', borderRadius: 8,
                    fontSize: 13, fontWeight: 600, flexShrink: 0,
                  }}>导航</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Input */}
      <div style={{ padding:'10px 16px 24px', background: CY.bg, flexShrink:0 }}>
        <div style={{
          background:'#fff', border:`1px solid ${CY.border}`,
          borderRadius: 25, padding:'12px 16px', display:'flex', alignItems:'center', gap: 12,
        }}>
          <span style={{ flex:1, fontSize: 14, color: CY.muted }}>问问附近适合去哪...</span>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke={CY.muted} strokeWidth="1.8"/>
            <circle cx="9" cy="10" r="1" fill={CY.muted}/>
            <circle cx="15" cy="10" r="1" fill={CY.muted}/>
            <path d="M8.5 14.5c1 1.2 2.2 1.8 3.5 1.8s2.5-.6 3.5-1.8" stroke={CY.muted} strokeWidth="1.6" strokeLinecap="round"/>
          </svg>
          <div style={{
            width: 28, height: 28, borderRadius: 14, background: CY.greenL,
            display:'flex', alignItems:'center', justifyContent:'center',
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke={CY.green} strokeWidth="2.5" strokeLinecap="round"/></svg>
          </div>
        </div>
      </div>
    </Phone>
  );
}

// ════════════════════════════════════════════════════════
// 12. PROFILE — 我的
// ════════════════════════════════════════════════════════
function ScreenProfile() {
  const stats = [
    { n: 12, l: '收藏' },
    { n: 23, l: '足迹' },
    { n: 5,  l: '路线' },
  ];
  const funcs = [
    { l:'我的收藏',
      i:(<svg width="26" height="26" viewBox="0 0 24 24" fill="none">
        <path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.9-6.2-3.3-6.2 3.3 1.2-6.9-5-4.9 6.9-1L12 2z" stroke={CY.green} strokeWidth="2" strokeLinejoin="round"/></svg>) },
    { l:'浏览历史',
      i:(<svg width="26" height="26" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke={CY.green} strokeWidth="2"/>
        <path d="M12 7v5l3 2" stroke={CY.green} strokeWidth="2" strokeLinecap="round"/></svg>) },
    { l:'我的路线',
      i:(<svg width="26" height="26" viewBox="0 0 24 24" fill="none">
        <circle cx="7"  cy="6" r="3" stroke={CY.green} strokeWidth="2"/>
        <circle cx="17" cy="18" r="3" stroke={CY.green} strokeWidth="2"/>
        <path d="M9 8c3 3 4 6 6 8" stroke={CY.green} strokeWidth="2" strokeLinecap="round" strokeDasharray="2 3"/></svg>) },
    { l:'离线地图',
      i:(<svg width="26" height="26" viewBox="0 0 24 24" fill="none">
        <path d="M12 3v14M6 11l6 6 6-6" stroke={CY.green} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="12" cy="3" r="2.2" fill={CY.green}/></svg>) },
    { l:'意见反馈',
      i:(<svg width="26" height="26" viewBox="0 0 24 24" fill="none">
        <path d="M4 5h16v11H8l-4 4V5z" stroke={CY.green} strokeWidth="2" strokeLinejoin="round"/>
        <circle cx="9" cy="11" r="1" fill={CY.green}/><circle cx="12" cy="11" r="1" fill={CY.green}/><circle cx="15" cy="11" r="1" fill={CY.green}/></svg>) },
    { l:'设置',
      i:(<svg width="26" height="26" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="3" stroke={CY.green} strokeWidth="2"/>
        <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09A1.65 1.65 0 008 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H2a2 2 0 110-4h.09A1.65 1.65 0 004.6 8a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V2a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H22a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z"
          stroke={CY.green} strokeWidth="1.6" strokeLinejoin="round" fill="none"/></svg>) },
  ];

  return (
    <Phone bg={CY.bg}>
      <CYStatusBar/>
      <div style={{ flex:1, overflowY:'auto', padding:'8px 14px 14px' }}>
        {/* User header */}
        <div style={{
          background: CY.greenL, borderRadius: 16, padding:'18px 18px',
          display:'flex', alignItems:'center', gap: 14, marginBottom: 12,
        }}>
          <div style={{
            width: 70, height: 70, borderRadius: 35, background:'#fff',
            display:'flex', alignItems:'center', justifyContent:'center',
          }}>
            <svg width="44" height="44" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" fill={CY.greenD}/>
              <path d="M4 22c1-5 4-7 8-7s7 2 8 7" fill={CY.greenD}/>
            </svg>
          </div>
          <div style={{ flex:1 }}>
            <div style={{ fontSize: 20, fontWeight: 800, color: CY.text }}>游客用户</div>
            <div style={{ fontSize: 14, color: CY.green, marginTop: 6, fontWeight: 500 }}>点击登录/注册</div>
          </div>
          <div style={{
            width: 40, height: 40, borderRadius: 20, background:'#F2F4F2',
            display:'flex', alignItems:'center', justifyContent:'center',
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="3" stroke={CY.textSub} strokeWidth="2"/>
              <path d="M19 12c0 .5 0 1-.1 1.5l2 1.6-2 3.5-2.4-1a7 7 0 01-2.6 1.5l-.4 2.5h-4l-.4-2.5a7 7 0 01-2.6-1.5l-2.4 1-2-3.5 2-1.6c-.1-.5-.1-1-.1-1.5s0-1 .1-1.5l-2-1.6 2-3.5 2.4 1a7 7 0 012.6-1.5l.4-2.5h4l.4 2.5a7 7 0 012.6 1.5l2.4-1 2 3.5-2 1.6c.1.5.1 1 .1 1.5z" stroke={CY.textSub} strokeWidth="1.5" fill="none"/>
            </svg>
          </div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M9 6l6 6-6 6" stroke={CY.muted} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>

        {/* Stats */}
        <div style={{
          background:'#fff', borderRadius: 16,
          display:'flex', padding:'18px 0', marginBottom: 12,
        }}>
          {stats.map((s, i) => (
            <div key={s.l} style={{
              flex:1, textAlign:'center',
              borderRight: i < stats.length-1 ? `1px solid ${CY.border}` : 'none',
            }}>
              <div style={{ fontSize: 24, fontWeight: 800, color: CY.text }}>{s.n}</div>
              <div style={{ fontSize: 13, color: CY.muted, marginTop: 4 }}>{s.l}</div>
            </div>
          ))}
        </div>

        {/* Common functions */}
        <div style={{ background:'#fff', borderRadius: 16, padding:'18px 18px 22px' }}>
          <div style={{ fontSize: 17, fontWeight: 800, color: CY.text, marginBottom: 18 }}>常用功能</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', rowGap: 22, columnGap: 10 }}>
            {funcs.map(f => (
              <div key={f.l} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap: 8 }}>
                <div style={{
                  width: 54, height: 54, borderRadius: 27, background: CY.greenLS,
                  display:'flex', alignItems:'center', justifyContent:'center',
                }}>{f.i}</div>
                <span style={{ fontSize: 12, color: CY.text }}>{f.l}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <TabBar active="me"/>
    </Phone>
  );
}

Object.assign(window, {
  ScreenRoutes, ScreenRouteDetail, ScreenPlaceDetail,
  ScreenChatEmpty, ScreenChatReply, ScreenProfile,
});
