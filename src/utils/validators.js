export function isValidCPF(cpf) {
  cpf = cpf.replace(/[^\d]+/g, '')
  if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false
  let soma = 0
  for (let i = 0; i < 9; i++) soma += parseInt(cpf.charAt(i)) * (10 - i)
  let resto = (soma * 10) % 11
  if (resto === 10 || resto === 11) resto = 0
  if (resto !== parseInt(cpf.charAt(9))) return false
  soma = 0
  for (let i = 0; i < 10; i++) soma += parseInt(cpf.charAt(i)) * (11 - i)
  resto = (soma * 10) % 11
  if (resto === 10 || resto === 11) resto = 0
  return resto === parseInt(cpf.charAt(10))
}

export function isValidCNPJ(cnpj) {
  cnpj = cnpj.replace(/[^\d]+/g, '')
  if (cnpj.length !== 14 || /^(\d)\1+$/.test(cnpj)) return false
  let t = cnpj.length - 2,
    d = cnpj.substring(t),
    d1 = parseInt(d.charAt(0)),
    d2 = parseInt(d.charAt(1)),
    calc = x => {
      let n = 0,
        r = 2
      for (let i = x.length - 1; i >= 0; i--) {
        n += x.charAt(i) * r++
        if (r > 9) r = 2
      }
      return n
    }
  let dg1 = calc(cnpj.substring(0, t)) % 11
  dg1 = dg1 < 2 ? 0 : 11 - dg1
  if (dg1 !== d1) return false
  let dg2 = calc(cnpj.substring(0, t + 1)) % 11
  dg2 = dg2 < 2 ? 0 : 11 - dg2
  return dg2 === d2
}

export function isPotentiallyMalicious(input) {
  if (typeof input !== 'string') {
    return false;
  }
  const lowerInput = input.toLowerCase();

  const sqlInjectionPatterns = new RegExp([
    // Operadores SQL comuns
    '\\b(?:select|insert|update|delete|drop|truncate|alter|create|union|exec|execute)\\b',
    // Comentários SQL e separadores de query
    '--|;|/\\*|\\*/',
    // Operadores lógicos
    '\\b(?:or|and)\\b\\s+\\d+=\\d+', // Ex: OR 1=1
    // Aspas e backticks escapados
    "['\"`]",
    // Keywords para bypass de login
    '\\b(?:admin|password)\\b',
    // Potenciais calls de sistema
    '\\b(?:xp_cmdshell|xp_regread)\\b' // Exemplo para SQL Server
  ].join('|'), 'i'); // 'i' para case-insensitive

  return sqlInjectionPatterns.test(lowerInput);
}