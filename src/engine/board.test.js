import { describe, it, expect } from 'vitest';
import {
  parsearSemilla,
  componerSemilla,
  generarTablero,
} from './board';

const LISTA = Array.from({ length: 30 }, (_, i) => `PALABRA${i}`);

describe('parsearSemilla / componerSemilla', () => {
  it('compone y parsea ida y vuelta', () => {
    const completa = componerSemilla('es_intermedio', 'K9A2');
    expect(completa).toBe('SI-K9A2');
    const p = parsearSemilla(completa);
    expect(p.vocabulario).toBe('es_intermedio');
    expect(p.semillaCorta).toBe('K9A2');
  });

  it('acepta forma sin guion y normaliza a mayúsculas', () => {
    expect(parsearSemilla('sik9a2').vocabulario).toBe('es_intermedio');
  });

  it('devuelve null ante semillas inválidas', () => {
    expect(parsearSemilla('ZZ-K9A2')).toBeNull(); // prefijo desconocido
    expect(parsearSemilla('SI-12')).toBeNull(); // muy corta
    expect(parsearSemilla('basura')).toBeNull();
  });
});

describe('generarTablero', () => {
  it('es determinista: misma semilla → mismo tablero', () => {
    const a = generarTablero('K9A2', LISTA);
    const b = generarTablero('K9A2', LISTA);
    expect(a).toEqual(b);
  });

  it('produce 25 cartas y la distribución 9/8/7/1', () => {
    const { palabrasTablero, mapaColores } = generarTablero('K9A2', LISTA);
    expect(palabrasTablero).toHaveLength(25);
    expect(mapaColores).toHaveLength(25);
    const conteo = mapaColores.reduce((acc, c) => {
      acc[c] = (acc[c] ?? 0) + 1;
      return acc;
    }, {});
    expect(conteo.beige).toBe(7);
    expect(conteo.rojo).toBe(1);
    // el equipo inicial tiene 9, el otro 8 (en algún orden verde/azul)
    expect([conteo.verde, conteo.azul].sort()).toEqual([8, 9]);
  });

  it('semillas distintas dan tableros distintos', () => {
    const a = generarTablero('K9A2', LISTA);
    const b = generarTablero('Z3X7', LISTA);
    expect(a).not.toEqual(b);
  });
});
