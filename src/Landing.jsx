import { useState } from 'react';
import './landing.css';
import hero from './assets/hero1.png'
import imageNash from './assets/Nash.jpg'


function Landing({onIniciarPartida}) {
  const [rondas, setRondas] = useState('3');
  const [idioma, setIdioma] = useState('es');

  // 1. Estados para NUEVA PARTIDA
  const [vocabularioCrear, setVocabularioCrear] = useState('es_es');
  const [palabrasCrear, setPalabrasCrear] = useState('');

  // 2. Estados independientes para ACCESO
  const [vocabularioAcceso, setVocabularioAcceso] = useState('es_es');
  const [palabrasAcceso, setPalabrasAcceso] = useState('');
  const [codigo, setCodigo] = useState('');

  const manejarCambioIdioma = (e) => {
    const nuevoIdioma = e.target.value;
    setIdioma(nuevoIdioma); // 1. Cambiamos el idioma

    // 2. Reseteamos el vocabulario al valor por defecto del nuevo idioma
    if (nuevoIdioma === 'es') setVocabularioAcceso('es_es');
    if (nuevoIdioma === 'en') setVocabularioAcceso('en_es');
    if (nuevoIdioma === 'de') setVocabularioAcceso('de_es');
  };
  
  const crearPartidaNueva = () => {
    onIniciarPartida({
      destino: 'tablero_principal',
      rondas,
      idioma,
      vocabulario: vocabularioCrear,
      palabras: palabrasCrear
    });
  };

  const accederPartidaExistente = () => {
    // Limpiamos espacios y pasamos a mayúsculas
    const semillaLimpia = codigo.trim().toUpperCase(); 

    // Verificación: Solo letras y números, mínimo 4, máximo 10 caracteres
    const esValida = /^[A-Z0-9]{4}$/.test(semillaLimpia);

    if (!esValida) {
      alert("La semilla debe tener 4 letras, sin espacios ni símbolos especiales.");
      return; // Detenemos la ejecución aquí
    }
    
    onIniciarPartida({
      destino: 'tablero_clave',
      semilla: semillaLimpia,
      vocabulario: vocabularioAcceso, 
      palabras: palabrasAcceso 
    });
  };

  return (
    <div className="landing-container">

        <header className='header-section'>
            <h1 className='game-title'>Indescifrable</h1>
            <img src={hero} alt="hero" className='hero-image-placeholder'/>
        </header>
        <main className='action-container'>
            <section className='setup-panel'>
                <h2>Nueva Partida</h2>

                <div className='form-group'>
                    <label>Rondas: </label>
                    <select value={rondas} onChange={(e)=>setRondas(e.target.value)}>
                        <option value="1">1</option>
                        <option value="3">3</option>
                        <option value="5">5</option>
                        <option value="10">10</option>
                    </select>
                </div>
                <div className='form-group'>
                    <label>Idioma: </label>
                    <select value={idioma} onChange={manejarCambioIdioma}>
                        <option value="es">Español</option>
                        <option value="en">English</option>
                        <option value="de">Deutsch</option>
                    </select>
                </div>
                
                <div className="form-group">
                    <label>Vocabulario: </label>
                    <select value={vocabularioCrear} onChange={(e) => setVocabularioCrear(e.target.value)}>

                    {/*ocupamos <></> para no crear divs innecesarios*/}    
                    {idioma === 'es' && (
                        <>
                            <option value="es_es">Estándar</option>
                            <option value="es_principiante">principiante</option>
                            <option value="es_intermedio">intermedio</option>
                            <option value="es_avanzado">avanzado</option>
                        </>
                    )}
                    {idioma === 'en' && (
                        <>
                            <option value="en_es">Standard</option>
                            <option value="en_principiante">begginer</option>
                            <option value="en_intermedio">intermediate</option>
                            <option value="en_avanzado">advanced</option>
                        </>
                    )}
                    {idioma === 'de' && (
                        <>
                            <option value="de_es">Standard</option>
                            <option value="de_principiante">Anfänger</option>
                            <option value="de_intermedio">Mittelstufe</option>
                            <option value="de_avanzado">Fortgeschrittene</option>
                        </>
                    )}
                    <option value="personalizado">Personalizado</option>
                    </select>
                </div>

                {/*si vocabulario el estado de vocabulario es personalizado, se despliega*/}
                {vocabularioCrear === 'personalizado' && (
                <div className='form-group'>
                    <label>Lista de palabras </label>
                    <textarea placeholder='agrega aquí tus palabras separadas por comas...' value={palabrasCrear}
                    onChange={(e)=>setPalabrasCrear(e.target.value)}></textarea>
                </div>
                )}

                <button className="btn-primary" onClick={crearPartidaNueva}>Iniciar Juego</button>
            </section>

            <section className='access-panel'>
                <h2>Panel de acceso (Capitanes)</h2>
                <p>Para ver la clave, necesitas la configuración exacta del tablero original:</p>

                <div className="form-group">
                    <label>Diccionario de la partida: </label>
                    <select value={vocabularioAcceso} onChange={(e) => setVocabularioAcceso(e.target.value)}>
                        
                        <optgroup label="Español">
                            <option value="es_es">Estándar</option>
                            <option value="es_principiante">Principiante</option>
                            <option value="es_intermedio">Intermedio</option>
                            <option value="es_avanzado">Avanzado</option>
                        </optgroup>
                        
                        <optgroup label="English">
                            <option value="en_es">Standard</option>
                            <option value="en_principiante">Beginner</option>
                            <option value="en_intermedio">Intermediate</option>
                            <option value="en_avanzado">Advanced</option>
                        </optgroup>
                        
                        <optgroup label="Deutsch">
                            <option value="de_es">Standard</option>
                            <option value="de_principiante">Anfänger</option>
                            <option value="de_intermedio">Mittelstufe</option>
                            <option value="de_avanzado">Fortgeschrittene</option>
                        </optgroup>

                        <optgroup label="Otros">
                            <option value="personalizado">Lista Personalizada</option>
                        </optgroup>

                    </select>
                </div>

                {/* EL TEXTAREA APARECE SI ELIGEN PERSONALIZADO */}
                {vocabularioAcceso === 'personalizado' && (
                    <div className="form-group">
                        <label>Palabras personalizadas:</label>
                        <textarea 
                            placeholder='Pega exactamente las mismas palabras separadas por coma...' 
                            value={palabrasAcceso} 
                            onChange={(e) => setPalabrasAcceso(e.target.value)}
                        />
                    </div>
                )}

                {/* LO DEMÁS SE QUEDA IGUAL */}
                <div className="form-group">
                    <label>Semilla de la partida:</label>
                    <input 
                        type="text"
                        maxLength={4}
                        placeholder='Ej. K9A2' 
                        value={codigo} 
                        onChange={(e) => setCodigo(e.target.value)}
                    />
                </div>

                <button className="btn-secondary" onClick={accederPartidaExistente}>
                    Ver Clave del Tablero
                </button>
            </section>
        </main>

        <footer className="info-section">
        
        <details>
          <summary>La Historia</summary>
          <p>Esta es la historia de Nacho. Nacho es un matemático que nunca se pudo titular porque le rechazaron su tesis en etnomatemáticas. Cansado de la academia decide alejarse de ella y dedicarse a ser editor de los juegos del periódico. Publica sudokus, sopas de letras y
            acertijos de matemáticas recreativas. Es un gran conocedor del horóscopo, los aliens, los reptilianos, la bolsa y particularmente las teorías de dominación mundial. Aunque nadie dudaba de su inteligencia, su temperamento osco hacía que nadie lo tomara demasiado en serio.
            De hecho, tiene prohibido entrar en el área de publicidad dado que durante los últimos meses estuvo molestando al trabajador responsable de poner anuncios en el periódico. Nacho le decía que cada uno de esos clasificados contenía un mensaje cifrado. En un principio, los
            editores se mostraron interesados en su idea dado que podría ser un buen escándalo, más se decepcionaron cuando aquél les mostró los supuestos mensajes: pintar, Bogotá, persiana, etc. Ni los más crédulos encontrarían un mensaje ahí. Él decía que realmente eran dos bandos
            contrarios los que utilizaban esta misma técnica de comunicación pero que no sabía si alguno de ellos era bueno o si ambos eran malos, si eran Iluminatis , o en el peor de los casos, agentes de la MASA. Sin embargo, tenía las de perder, pues ya hacía años que ese mismo
            periódico había publicado una noticia super viral, la cual se titulaba “La era de la post-Criptografía; el problema criptográfico se zanja con la QuantumKey ”.
            Nacho llegó a tal obsesión que decidido probar su punto. Se infiltró en la sección de imprenta y modificó la versión final para que en primera plana apareciera una tabla 5x5 con palabras que parecían aleatorias. Realmente lo que hizo fue combinar las 8 palabras de un bando junto con
            las 7 palabras del otro bando y mezclarlas con otras 10 palabras para mostrar a los emisores que habían sido descubiertos. 
            Es tal el olvido por el periódico que ni los que transportaban los bultos le dieron importancia.  Incluso tuvieron que pasar algunas horas para que la gente notara la anomalía. Todo el mundo se volvió loco, ¿qué rayos significaban esas palabras? El periódico se agotó por primera vez
            en más de 100 años. Las teorías no tardaron en esparcirse. Contiguamente, los Iluminatis y la MASA se arrancaban los pelos. Cómo era posible que alguien captara su estrategia. ¿Quién logrará transmitir más rápidamente el mensaje, los Ilumintis o la MASA?
            </p>
        </details>

        <details>
          <summary>Instrucciones de Juego</summary>
          <ul>
            <li>Creen dos equipos: Los Iluminatis (verde) y La MASA (azul). Cada equipo selecciona a un integrante para fungir como emisor del mensaje (Jefe); el resto del equipo serán los receptores (Agentes).</li>
            <li>El equipo que inicia deberá adivinar 8 tarjetas. El otro equipo, 7.</li>
            <li>El tablero consta de 25 tarjetas: 8/7 tarjetas de los equipos, 9 fichas beige (civiles) y 1 roja (el sistema/asesino).</li>
            <li>En cada ronda, el emisor dirá una palabra que relacione la mayor cantidad posible de tarjetas de su equipo en el tablero, seguida de la cantidad de tarjetas. Ejemplo: “Verde, 3”. <em>Regla:</em> No se puede decir ninguna palabra que esté escrita en el tablero.</li>
            <li>Los receptores tienen un máximo de 1 minuto para debatir. Seleccionarán las tarjetas <strong>una por una</strong>.</li>
            <li>Si tocan una tarjeta de su color, pueden seguir adivinando. Si tocan una tarjeta del rival o una beige, el turno termina inmediatamente.</li>
            <li>La ronda termina cuando un equipo encuentra todas sus tarjetas o si alguien toca la tarjeta roja (pierden automáticamente).</li>
            <li>Gana la partida el equipo con más rondas a su favor.</li>
          </ul>
        </details>

        <details>
            <summary>Disclaimer</summary>
            <p>El siguiente juego está basado en el juego de mesa Codenames y la historia del matemático Nash</p>
            <p>John Forbes Nash</p>
            <p>John Nash fue un brillante matemático estadounidense (famoso por la película "Una mente brillante") que ganó el Premio Nobel de Economía gracias a sus aportes a la Teoría de Juegos. La mente de John Nash operaba bajo una necesidad constante de encontrar estructura,
                lo que lo llevó a ver patrones en absolutamente todo. Por el lado bueno, esta capacidad le permitió encontrar el orden matemático dentro del comportamiento humano, formulando el Equilibrio de Nash y descubriendo lógicas predecibles donde otros solo veían caos. Sin embargo,
                esa misma hipervigilancia cognitiva le jugó en contra: su cerebro comenzó a forzar conexiones donde no existían, llevándolo a creer que textos cotidianos, números sueltos o artículos de periódicos contenían mensajes cifrados y conspiraciones políticas. Su genialidad matemática
                y el desarrollo de su esquizofrenia partieron del mismo punto: una mente que simplemente no podía dejar de intentar descifrar el ruido a su alrededor.</p>
            <img src={imageNash} alt="Nash" />
        </details>

      </footer>

    </div>
  );
}

export default Landing;