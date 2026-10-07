/* Deterministic motion design. Paper figures are drawn directly from the published crops.
   Open index.html through an HTTP server rooted at the repository. renderFrame(seconds)
   renders an exact frame; no wall-clock animations or random assets are used. */
"use strict";
const W=1920,H=1080, DURATION=90;
const canvas=document.getElementById('film'), c=canvas.getContext('2d',{alpha:false});
const C={bg:'#04090f',white:'#f2f4ee',muted:'#96aab4',gold:'#e7c77c',mint:'#70ead3',red:'#fa827b',blue:'#8caeed'};
const F={sans:'Montserrat, Arial, sans-serif',body:'"Liberation Sans", Arial, sans-serif',serif:'"STIX Two Text", Georgia, serif',zh:'"Noto Sans CJK SC", sans-serif',mono:'"Source Code Pro", monospace'};
const clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v));
const ease=v=>{v=clamp(v);return v*v*(3-2*v)};
const out=v=>1-Math.pow(1-clamp(v),3);
const lerp=(a,b,t)=>a+(b-a)*t;
let rngState=681923;
function rand(){rngState=(Math.imul(1664525,rngState)+1013904223)>>>0;return rngState/4294967296;}
const stars=Array.from({length:160},()=>({x:rand()*W,y:rand()*H,r:rand()*1.5+.35,s:rand()*.6+.15,p:rand()*Math.PI*2}));
const grain=document.createElement('canvas');grain.width=480;grain.height=270;
const gc=grain.getContext('2d'), pixels=gc.createImageData(480,270);
for(let i=0;i<pixels.data.length;i+=4){let k=Math.floor(rand()*255);pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=k;pixels.data[i+3]=12;}
gc.putImageData(pixels,0,0);
const shots=[
 {id:'question',start:0,end:8,label:'01 / THE QUESTION',draw:question},
 {id:'trajectory',start:8,end:20,label:'02 / THE TRAJECTORY',draw:trajectory},
 {id:'scale',start:20,end:30,label:'03 / THE BENCHMARK',draw:scale},
 {id:'risks',start:30,end:43,label:'04 / TWO SOURCES OF RISK',draw:risks},
 {id:'method',start:43,end:57,label:'05 / THE FRAMEWORK',draw:method},
 {id:'results',start:57,end:71,label:'06 / THE EVIDENCE',draw:results},
 {id:'skills',start:71,end:81,label:'07 / THE SKILL LAYER',draw:skills},
 {id:'closing',start:81,end:90,label:'',draw:closing},
];
const imgs={};let storyboard;
function font(size,weight=400,family=F.sans){c.font=`${weight} ${size}px ${family}`;}
function text(str,x,y,size=32,color=C.white,weight=500,align='left',family=F.sans){font(size,weight,family);c.fillStyle=color;c.textAlign=align;c.textBaseline='alphabetic';c.fillText(str,x,y);}
function fitText(str,x,y,maxWidth,size=32,color=C.white,weight=500,align='left',family=F.sans){font(size,weight,family);const width=c.measureText(str).width;text(str,x,y,Math.min(size,size*maxWidth/width),color,weight,align,family);}
function tracked(str,x,y,size=18,color=C.muted,spacing=4,align='left'){
 font(size,500);let widths=[...str].map(s=>c.measureText(s).width+spacing);let width=widths.reduce((a,b)=>a+b,0)-spacing;
 if(align==='center')x-=width/2;else if(align==='right')x-=width;
 c.fillStyle=color;c.textAlign='left';c.textBaseline='alphabetic';[...str].forEach((s,i)=>{c.fillText(s,x,y);x+=widths[i]});
}
function line(x1,y1,x2,y2,color=C.mint,width=2,alpha=1){c.save();c.globalAlpha*=alpha;c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.strokeStyle=color;c.lineWidth=width;c.stroke();c.restore();}
function glow(x,y,r,color,alpha=.22){c.save();c.globalAlpha*=alpha;let g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,color);g.addColorStop(1,'transparent');c.fillStyle=g;c.fillRect(x-r,y-r,r*2,r*2);c.restore();}
function round(x,y,w,h,r=16,fill='#0c1720',stroke=null){c.beginPath();c.roundRect(x,y,w,h,r);if(fill){c.fillStyle=fill;c.fill()}if(stroke){c.strokeStyle=stroke;c.lineWidth=1;c.stroke()}}
function ring(x,y,r,color,width=2,alpha=1){c.save();c.globalAlpha*=alpha;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.strokeStyle=color;c.lineWidth=width;c.stroke();c.restore();}
function dot(x,y,r,color=C.mint){c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fillStyle=color;c.fill()}
function entrance(u,delay,fn,duration=.8){let p=out((u-delay)/duration);if(p<=0)return;c.save();c.globalAlpha*=p;c.translate(0,(1-p)*24);fn(p);c.restore();}
function paper(name,x,y,w,h,crop=null){
 c.save();c.shadowColor='#0009';c.shadowBlur=40;c.shadowOffsetY=18;round(x,y,w,h,16,'#fff');c.restore();
 c.save();c.beginPath();c.roundRect(x+12,y+12,w-24,h-24,5);c.clip();c.fillStyle='white';c.fillRect(x,y,w,h);
 const image=imgs[name],q=crop||[0,0,image.width,image.height],scale=Math.min((w-32)/q[2],(h-32)/q[3]);
 const dw=q[2]*scale,dh=q[3]*scale;
 c.drawImage(image,q[0],q[1],q[2],q[3],x+(w-dw)/2,y+(h-dh)/2,dw,dh);c.restore();
}
function background(t){
 c.fillStyle=C.bg;c.fillRect(0,0,W,H);
 let g=c.createRadialGradient(970+120*Math.sin(t*.05),480,10,960,490,1080);
 g.addColorStop(0,'#102730');g.addColorStop(.48,'#091621');g.addColorStop(1,'#03070d');c.fillStyle=g;c.fillRect(0,0,W,H);
 glow(1300+180*Math.sin(t*.12),400,670,C.mint,.028);glow(520,650,700,C.gold,.035);
 // A slowly moving perspective grid gives the film depth without competing with the data.
 c.save();c.globalAlpha=.14;
 for(let i=-8;i<=8;i++)line(960+i*44,540,960+i*245,1080,'#366b78',.65);
 for(let j=0;j<13;j++){let z=((j/13+t*.011)%1);let y=540+Math.pow(z,2)*560;line(0,y,W,y,'#3e7180',.65,Math.max(.1,z));}
 c.restore();
 for(const s of stars){let x=(s.x+t*s.s*3)%W,y=s.y+Math.sin(t*.2+s.p)*12;let a=.15+.28*(.5+.5*Math.sin(t*.5+s.p));c.save();c.globalAlpha=a;dot(x,y,s.r,s.p>3?C.gold:C.mint);c.restore();}
 c.save();c.globalAlpha=.32;c.drawImage(grain,0,0,W,H);c.restore();
 let v=c.createRadialGradient(960,520,240,960,520,1150);v.addColorStop(0,'transparent');v.addColorStop(1,'#0009');c.fillStyle=v;c.fillRect(0,0,W,H);
}
function chrome(t,shot,poster){
 if(poster)return;
 tracked('LPS / RESEARCH FILM',72,56,15,'#a9b8c0',3);
 tracked('NEURIPS 2026',1848,56,15,C.gold,3,'right');line(72,78,1848,78,'#527582',1,.35);
 if(shot.label)tracked(shot.label,92,126,17,C.gold,3);
 line(72,1057,1848,1057,'#4a6572',1,.45);line(72,1057,72+1776*clamp(t/DURATION),1057,C.mint,2,.9);
 dot(72+1776*clamp(t/DURATION),1057,3,C.mint);
}
function question(u){
 const danger=ease((u-2.3)/1.1);
 glow(960,455,330,C.mint,.10*(1-danger));glow(1170,625,350,C.red,.15*danger);
 entrance(u,.3,()=>tracked('TASK COMPLETE',960,265,30,C.mint,9,'center'));
 entrance(u,2.45,()=>{text('AT WHAT COST?',960,447,142,C.white,650,'center');text('安全结果，可能掩盖过程风险',960,516,37,C.gold,400,'center',F.zh)});
 c.save();c.globalAlpha*=1-danger;ring(960,480,82,C.mint,3);line(918,478,952,511,C.mint,5);line(952,511,1005,449,C.mint,5);c.restore();
 const points=13,yy=687,range=1490;
 line(215,yy,1705,yy,'#537c86',2,.55);
 for(let i=0;i<points;i++){
  const x=215+i*range/(points-1),bad=i===8&&danger>.1,co=bad?C.red:C.mint;
  const p=clamp((u-.35)*3-i);c.save();c.globalAlpha*=p;dot(x,yy,i===points-1?9:6,co);ring(x,yy,14,co,1,.4);
  if(bad){ring(x,yy,24+18*(.5+.5*Math.sin(u*4)),co,2,danger*.7);line(x,yy,x+115,yy+97,co,2,danger);dot(x+115,yy+97,6,co);text('UNSAFE COMMITMENT',x+135,yy+105,20,co,500);}
  c.restore();
 }
 entrance(u,4.4,()=>{tracked('LOOK THROUGH THE ENTIRE TRAJECTORY',960,870,20,C.muted,5,'center')});
}
function trajectory(u){
 entrance(u,0,()=>{text('ONE ASSUMPTION.',115,266,83,C.white,650);text('A CHAIN OF CONSEQUENCES.',115,363,73,C.gold,500)});
 tracked('ILLUSTRATIVE TRAJECTORY',1810,174,16,C.muted,2,'right');
 const labels=['SEARCH','SELECT','PLAN','AUTHORIZE','EXECUTE','OBSERVE','FINISH'];
 const progress=clamp((u-.9)/7.6)*6,y=575;
 for(let i=0;i<7;i++){
  let x=190+i*256,bad=i>=1,co=bad?C.red:C.mint,active=progress>=i;
  if(i<6){line(x,y,x+256,y,'#3d5662',2,.7);let seg=clamp(progress-i);line(x,y,x+256*seg,y,co,3,.95);}
  glow(x,y,65,co,active?.17:.025);ring(x,y,31,active?co:'#3e5663',2);dot(x,y,active?9:4,active?co:'#6c8590');
  text(labels[i],x,y+72,20,active?C.white:C.muted,500,'center');
  text(String(i+1).padStart(2,'0'),x,y-60,19,C.muted,500,'center',F.mono);
 }
 let xx=190+progress*256;glow(xx,y,65,progress<1?C.mint:C.red,.32);dot(xx,y,7,C.white);
 entrance(u,2.4,()=>{round(332,760,1220,86,12,'#131921','#9f5c5255');text('UNVERIFIED DETAIL',400,814,24,C.red,600);text('→',755,817,38,C.gold,400);text('UNSAFE COMMITMENT',833,814,24,C.white,600)});
}
function scale(u){
 entrance(u,.05,()=>tracked('BUILT TO EXAMINE PLANNING SAFETY',120,224,22,C.gold,5));
 const n=Math.round(570*out(u/1.8));
 glow(490,465,370,C.mint,.07);text(String(n),470,583,328,C.white,600,'center');tracked('BASE TEST CASES',470,659,27,C.mint,7,'center');
 line(884,291,884,757,'#5e8390',1,.45);
 const data=[['7','DOMAINS',1020,425],['9','RISK TYPES',1470,425],['40','SKILL VARIANTS',1250,707]];
 data.forEach(([n,label,x,y],i)=>entrance(u,.5+i*.35,()=>{text(n,x,y,144,C.gold,500,'center');tracked(label,x,y+57,21,C.white,3,'center')}));
 entrance(u,2,()=>{text('252 benign',291,790,31,C.mint,500,'center');text('+',490,790,31,C.muted,400,'center');text('318 adversarial',693,790,31,C.red,500,'center')});
 const labels=['WEB','CODE','FILES','MEDIA','SOCIAL','OS','OFFICE'];
 labels.forEach((label,i)=>entrance(u,2.5+i*.1,()=>{round(143+i*237,847,210,47,7,'#0b1b25','#42667466');tracked(label,248+i*237,878,15,C.muted,2,'center')}));
}
function risks(u){
 entrance(u,0,()=>text('WHERE PLANS BREAK.',960,236,88,C.white,600,'center'));
 const groups=[{x:100,color:C.mint,title:'BENIGN',n:'252',rows:[['FA','Ambiguous assumptions'],['OC','Over-compliance'],['TS','Unsafe task ordering'],['IP','Resource waste']]},{x:995,color:C.red,title:'ADVERSARIAL',n:'318',rows:[['HS','Harmless-looking subtasks'],['MT','Multi-turn steering'],['EB','Poisoned observations'],['RC','Race conditions'],['PI','Prompt injection']]}];
 groups.forEach((g,j)=>{
  entrance(u,.3+j*.35,()=>{round(g.x,304,825,569,18,'#0a161fdd',g.color+'55');line(g.x+28,306,g.x+797,306,g.color,2,.8);tracked(g.title,g.x+46,379,25,g.color,5);text(g.n,g.x+776,384,62,C.white,500,'right');text('USER-INDUCED RISKS',g.x+46,422,16,C.muted,500)});
  g.rows.forEach(([code,label],i)=>entrance(u,.9+j*.6+i*.35,()=>{const yy=493+i*77;round(g.x+45,yy-26,65,39,5,g.color+'13',g.color+'55');text(code,g.x+77,yy+2,21,g.color,500,'center',F.mono);text(label,g.x+144,yy+2,28,C.white,450)}));
 });
}
function method(u){
 const phase=u<5?0:u<9?1:2;
 entrance(u,.1,()=>{text('GENERATE.',98,290,71,C.white,600);text('INTERACT.',98,391,71,C.white,600);text('EVALUATE.',98,492,71,C.gold,600)});
 entrance(u,.8,()=>{text('Full trajectories.',102,626,34,C.mint,450);text('Case-specific criteria.',102,678,32,C.white,450);tracked('PAPER / FIGURE 3',102,793,17,C.muted,3)});
 const iw=imgs.overview.width,ih=imgs.overview.height;
 const full=[0,0,iw,ih],top=[.5*iw,.035*ih,.5*iw,.455*ih],bottom=[.384*iw,.524*ih,.616*iw,.476*ih];
 let q=full;if(u>=4.3&&u<8.6){let p=ease((u-4.3)/1.2);q=full.map((v,i)=>lerp(v,top[i],p));}else if(u>=8.6){let p=ease((u-8.6)/1.3);q=top.map((v,i)=>lerp(v,bottom[i],p));}
 entrance(u,.35,()=>{paper('overview',691,185,1130,711,q);});
 const labels=['BENCHMARK CONSTRUCTION & EVALUATION','MULTI-AGENT CASE CONSTRUCTION','TRAJECTORY-LEVEL SAFETY EVALUATION'];
 tracked(labels[phase],1254,932,16,C.gold,2,'center');
}
function results(u){
 const tableReveal=ease((u-9.7)/.7);
 c.save();c.globalAlpha*=1-tableReveal;
 entrance(u,.15,()=>paper('results',112,183,660,684));
 tracked('PAPER / FIGURE 1',442,908,16,C.muted,3,'center');
 entrance(u,.35,()=>{text('SAFETY GAPS.',872,255,71,C.white,600);text('IN PLAIN SIGHT.',872,342,71,C.gold,500)});
 entrance(u,1,()=>tracked('SUCCESS-CONDITIONED SAFE RATE',875,406,17,C.muted,2));
 entrance(u,1.25,()=>{text((58.55*out((u-1.25)/1.5)).toFixed(2)+'%',872,540,131,C.mint,500);tracked('BENIGN RISKS',881,589,22,C.white,3)});
 entrance(u,2.4,()=>{text((95.77*out((u-2.4)/1.5)).toFixed(2)+'%',872,744,131,C.red,500);tracked('ADVERSARIAL RISKS',881,793,22,C.white,3)});
 entrance(u,3.5,()=>{text('Claude-4.5-Sonnet · risk-category averages',877,859,23,C.white,400);text('Paper results on the original case revision',877,904,22,C.muted,400)});
 c.restore();
 if(tableReveal>0){
  c.save();c.globalAlpha*=tableReveal;
  text('THE FULL PICTURE.',122,221,68,C.white,600);
  tracked('13 MODELS / 9 RISK TYPES',1795,215,21,C.gold,3,'right');
  paper('table',116,265,1688,618);
  // A translucent reading guide sits over the original Claude-4.5-Sonnet row.
  const s=Math.min((1688-32)/imgs.table.width,(618-32)/imgs.table.height), imageLeft=116+(1688-imgs.table.width*s)/2, imageTop=265+(618-imgs.table.height*s)/2;
  c.save();c.globalAlpha*=.9;round(imageLeft+3,imageTop+402.5*s,(imgs.table.width-6)*s,42.25*s,2,'#e7c77c24','#b08736aa');c.restore();
  text('Table 3 · SR_success = safe / (safe + unsafe) · Risk-category averages',960,924,23,C.muted,400,'center');
  c.restore();
 }
}
function skills(u){
 entrance(u,.05,()=>{text('SKILLS CHANGE',117,235,79,C.white,600);text('THE DECISION LAYER.',117,329,79,C.gold,500)});
 entrance(u,.55,()=>{text('40',1701,245,108,C.mint,550,'center');tracked('PAIRED CASES',1700,297,19,C.white,2,'center')});
 entrance(u,1,()=>paper('skills',117,403,1686,471));
 entrance(u,1.7,()=>{tracked('TABLE 5 / INDEPENDENT PAIRED RERUNS',123,915,17,C.muted,3);tracked('FA · OC · TS · PI   /   10 CASES EACH',1799,915,18,C.gold,2,'right')});
}
function closing(u){
 const appear=out(u/1.5);glow(960,456,720,C.mint,.04+.08*appear);
 for(let j=0;j<4;j++){let r=180+j*97+u*7;ring(960,464,r,C.mint,.8,.025*(4-j));}
 entrance(u,0,()=>tracked('ACCEPTED AT NEURIPS 2026',960,230,25,C.gold,6,'center'));
 entrance(u,.35,()=>text('LPS-Bench',960,439,184,C.white,600,'center'));
 line(605,484,1315,484,C.gold,2,clamp((u-.6)/1.3));
 entrance(u,.9,()=>{tracked('SAFETY AT EVERY STEP',960,569,39,C.gold,5,'center');text('评估长程规划中的每一步安全',960,635,34,C.muted,400,'center',F.zh)});
 entrance(u,1.55,()=>tracked('570 CASES    /    7 DOMAINS    /    9 RISK TYPES',960,720,21,C.white,3,'center'));
 entrance(u,2.1,()=>{text('Explore the benchmark.',960,813,33,C.mint,500,'center');text('github.com/tychenn/LPS-Bench',960,865,28,C.white,400,'center',F.body);text('huggingface.co/datasets/tianyyuu/LPS-Bench',960,910,24,C.muted,400,'center',F.body)});
}
function subtitles(t){
 const cue=storyboard.captions.find(q=>t>=q.start&&t<q.end);if(!cue)return;
 const opacity=Math.min(out((t-cue.start)/.16),out((cue.end-t)/.13));
 c.save();c.globalAlpha=opacity;
 let grad=c.createLinearGradient(0,935,0,1044);grad.addColorStop(0,'#03070d00');grad.addColorStop(.3,'#03070deb');grad.addColorStop(1,'#03070deb');c.fillStyle=grad;c.fillRect(0,935,W,108);
 fitText(cue.en,960,984,1740,29,'#f0f3f2',400,'center',F.body);
 fitText(cue.zh,960,1026,1740,27,'#c5d4d6',400,'center',F.zh);
 c.restore();
}
function renderFrame(t,options={}){
 t=clamp(t,0,DURATION-.001);background(t);
 for(const shot of shots){if(t<shot.start-.4||t>shot.end+.4)continue;let a=ease((t-shot.start+.35)/.7)*(shot.end===90?1:ease((shot.end+.25-t)/.6));if(a<=0)continue;c.save();c.globalAlpha=a;shot.draw(Math.max(0,t-shot.start));c.restore();}
 const active=shots.find(s=>t>=s.start&&t<s.end)||shots[shots.length-1];
 chrome(t,active,options.poster);if(!options.poster)subtitles(t);
 // Brief warm edge bloom links scene boundaries, without full-screen flashes.
 if(!options.poster)for(const shot of shots.slice(1)){let d=Math.abs(t-shot.start);if(d<.45){glow(30,480,580,C.gold,.07*(1-d/.45));}}
 window.currentFrameTime=t;
}
window.renderFrame=renderFrame;
window.ready=(async()=>{
 storyboard=await (await fetch('../video_storyboard.json')).json();
 await Promise.all(Object.entries({overview:'paper-overview.png',results:'paper-results.png',table:'paper-results-table.png',skills:'paper-skills-table.png'}).map(async([key,name])=>{const image=new Image();image.src='../../site/assets/'+name;await image.decode();imgs[key]=image;}));
 await document.fonts.ready;renderFrame(Number(new URLSearchParams(location.search).get('t')||85));return true;
})();
