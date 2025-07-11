// Configuração do commitlint para padronização de commits
module.exports = {
  // Estender configuração convencional
  extends: ['@commitlint/config-conventional'],
  
  // Configurações personalizadas
  rules: {
    // Tipo do commit é obrigatório
    'type-enum': [
      2, // Nível de erro
      'always',
      [
        'feat',      // Nova funcionalidade
        'fix',       // Correção de bug
        'docs',      // Documentação
        'style',     // Formatação, sem mudança de código
        'refactor',  // Refatoração de código
        'perf',      // Melhoria de performance
        'test',      // Adição ou correção de testes
        'chore',     // Tarefas de manutenção
        'ci',        // Mudanças de CI/CD
        'build',     // Mudanças no sistema de build
        'revert',    // Reverter commit anterior
        'release',   // Release de versão
        'deps',      // Atualização de dependências
        'config',    // Mudanças de configuração
        'data',      // Mudanças relacionadas a dados
        'ml',        // Mudanças em modelos de ML
        'ui',        // Mudanças na interface
        'api',       // Mudanças na API
        'db',        // Mudanças no banco de dados
        'security'   // Correções de segurança
      ]
    ],
    
    // Escopo é opcional mas quando usado deve estar na lista
    'scope-enum': [
      2,
      'always',
      [
        'auth',        // Autenticação
        'dashboard',   // Dashboard
        'pets',        // Gestão de pets
        'users',       // Gestão de usuários
        'analytics',   // Análises e ML
        'reports',     // Relatórios
        'export',      // Exportação
        'import',      // Importação
        'admin',       // Painel administrativo
        'config',      // Configurações
        'db',          // Banco de dados
        'ui',          // Interface do usuário
        'api',         // API
        'tests',       // Testes
        'docs',        // Documentação
        'ci',          // CI/CD
        'deps',        // Dependências
        'security',    // Segurança
        'performance', // Performance
        'backup',      // Backup/Restore
        'logs',        // Sistema de logs
        'notifications', // Notificações
        'visualization', // Visualizações
        'ml',          // Machine Learning
        'core'         // Funcionalidades core
      ]
    ],
    
    // Configurações de formato
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    'scope-case': [2, 'always', 'lower-case'],
    'subject-case': [2, 'always', 'sentence-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'header-max-length': [2, 'always', 100],
    'body-leading-blank': [1, 'always'],
    'body-max-line-length': [2, 'always', 100],
    'footer-leading-blank': [1, 'always'],
    'footer-max-line-length': [2, 'always', 100],
    
    // Referências a issues
    'references-empty': [1, 'never'],
  },
  
  // Configurações do parser
  parserPreset: {
    parserOpts: {
      // Padrão para detectar referências a issues
      issuePrefixes: ['#', 'gh-'],
      referenceActions: [
        'close',
        'closes',
        'closed',
        'fix',
        'fixes',
        'fixed',
        'resolve',
        'resolves',
        'resolved'
      ]
    }
  },
  
  // Configurações para ignorar commits específicos
  ignores: [
    // Ignorar commits de merge
    (commit) => commit.includes('Merge'),
    // Ignorar commits automáticos do dependabot
    (commit) => commit.includes('dependabot'),
    // Ignorar commits de release automático
    (commit) => commit.includes('chore(release)'),
  ],
  
  // Configurações de help
  helpUrl: 'https://github.com/conventional-changelog/commitlint/#what-is-commitlint',
  
  // Formatter personalizado para mensagens
  formatter: '@commitlint/format',
  
  // Configurações adicionais
  prompt: {
    messages: {
      skip: ':pular',
      max: 'máximo %d caracteres',
      min: 'mínimo %d caracteres',
      emptyWarning: 'não pode estar vazio',
      upperLimitWarning: 'acima do limite',
      lowerLimitWarning: 'abaixo do limite'
    },
    questions: {
      type: {
        description: 'Selecione o tipo de mudança que você está commitando:',
        enum: {
          feat: {
            description: 'Nova funcionalidade',
            title: 'Features'
          },
          fix: {
            description: 'Correção de bug',
            title: 'Bug Fixes'
          },
          docs: {
            description: 'Mudanças apenas na documentação',
            title: 'Documentation'
          },
          style: {
            description: 'Mudanças que não afetam o código (espaços, formatação, etc)',
            title: 'Styles'
          },
          refactor: {
            description: 'Mudança de código que não corrige bug nem adiciona funcionalidade',
            title: 'Code Refactoring'
          },
          perf: {
            description: 'Mudança que melhora a performance',
            title: 'Performance Improvements'
          },
          test: {
            description: 'Adição de testes ou correção de testes existentes',
            title: 'Tests'
          },
          chore: {
            description: 'Outras mudanças que não modificam src ou arquivos de teste',
            title: 'Chores'
          }
        }
      },
      scope: {
        description: 'Qual é o escopo desta mudança (ex: auth, dashboard, pets)?'
      },
      subject: {
        description: 'Escreva uma descrição curta e imperativa da mudança:'
      },
      body: {
        description: 'Forneça uma descrição mais longa da mudança:'
      },
      isBreaking: {
        description: 'Há alguma mudança que quebra compatibilidade?'
      },
      breakingBody: {
        description: 'Um commit BREAKING CHANGE requer um corpo. Por favor, insira uma descrição mais longa do próprio commit:'
      },
      breaking: {
        description: 'Descreva as mudanças que quebram compatibilidade:'
      },
      isIssueAffected: {
        description: 'Esta mudança afeta alguma issue aberta?'
      },
      issuesBody: {
        description: 'Se issues são fechadas, o commit requer um corpo. Por favor, insira uma descrição mais longa do próprio commit:'
      },
      issues: {
        description: 'Adicione referências de issues (ex: "fix #123", "re #123".):'
      }
    }
  }
};
