/** Deliberately simple local heuristics. Not semantic analysis or legal advice. */
const stop = new Set('a an the and or of in on at for to with from this that we i our your is be it as please can could also add make include build create need want'.split(' '));
export const lines = text => text.split('\n').map(x=>x.trim()).filter(Boolean).slice(0,40);
export const tokens = text => new Set(text.toLowerCase().replace(/[^a-z0-9\s]/g,' ').split(/\s+/).filter(x=>x.length>2&&!stop.has(x)));
export function analyze(scope,requests) {
  const agreed=lines(scope);
  return lines(requests).map((request,index)=>{
    const terms=tokens(request);let best={score:0,line:'',matches:[]};
    for(const line of agreed){const original=tokens(line),matches=[...terms].filter(x=>original.has(x));const score=matches.length/Math.max(1,terms.size);if(score>best.score)best={score,line,matches};}
    return {id:index,request,reference:best.line,matches:best.matches,score:best.score,status:'review',hours:''};
  });
}
export function pricing(items,rate,currency) {
  const changes=items.filter(x=>x.status==='change');
  if (!changes.length) return {text:'No changes selected',total:null,error:''};
  const anyHours=changes.some(x=>String(x.hours).trim()!=='');
  if (String(rate).trim()===''&&!anyHours) return {text:'Estimate not supplied',total:null,error:''};
  if (String(rate).trim()===''||!Number.isFinite(Number(rate))||Number(rate)<=0||Number(rate)>100000) return {text:'Estimate incomplete',total:null,error:'Enter a positive hourly rate up to 100,000, or clear all estimate fields.'};
  if(changes.some(x=>String(x.hours).trim()===''||!Number.isFinite(Number(x.hours))||Number(x.hours)<=0||Number(x.hours)>10000))return {text:'Estimate incomplete',total:null,error:'Every selected change needs positive hours up to 10,000 before a total can be included.'};
  const hours=changes.reduce((sum,x)=>sum+Number(x.hours),0),total=Math.round(hours*Number(rate)*100)/100;
  return {text:new Intl.NumberFormat('en-US',{style:'currency',currency}).format(total),total,hours,error:''};
}
export function makeDraft({project,scope,items,rate,currency}) {
  const quote=pricing(items,rate,currency),changes=items.filter(x=>x.status==='change'),included=items.filter(x=>x.status==='include'),review=items.filter(x=>x.status==='review');
  let out=`Change request: ${project.trim()||'Untitled project'}\n\nFor discussion and approval. This draft does not change an existing agreement.\n\nORIGINAL AGREED SCOPE\n${lines(scope).map((x,i)=>`${i+1}. ${x}`).join('\n')}\n`;
  for(const [title,rows] of [['REQUESTS MARKED WITHIN SCOPE',included],['PROPOSED CHANGES',changes],['STILL TO CLARIFY',review]]) {
    if(rows.length) out+=`\n${title}\n`+rows.map((x,i)=>`${i+1}. ${x.request}\n   Original scope reference: ${x.reference||'No shared-keyword reference found; confirm against agreement.'}${title==='PROPOSED CHANGES'&&quote.total!==null?`\n   Proposed effort: ${Number(x.hours)} hours`:''}`).join('\n')+'\n';
  }
  out+=quote.total!==null?`\nUSER-SUPPLIED ESTIMATE\n${quote.hours} hours at ${currency} ${Number(rate).toFixed(2)}/hour = ${quote.text}\nTaxes, payment terms and schedule are not included; agree them separately.\n`:'\nESTIMATE\nNo complete estimate supplied. Effort, pricing and schedule remain to be agreed.\n';
  out+='\nPlease confirm the scope interpretation and selected changes before any additional work begins.\n\nPrepared using local keyword suggestions and user decisions. Not a contract or legal review.\n';return out;
}
