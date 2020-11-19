#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Sanitation Explorer: Sustainable design of non-sewered sanitation technologies
Copyright (C) 2020, Sanitation Explorer Development Group

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>
    Joy Cheung

This module is under the UIUC open-source license. Please refer to 
https://github.com/QSD-for-WaSH/sanitation/blob/master/LICENSE.txt
for license details.
'''


import thermosteam as tmo
from chemicals.elements import (
    mass_fractions as get_mass_frac,
    molecular_weight as get_MW
    )

__all__ = ('Component',)

_chemical_fields = tmo._chemical._chemical_fields
_checked_properties = tmo._chemical._checked_properties
display_asfunctor = tmo._chemical.display_asfunctor
chemical_units_of_measure = tmo._chemical.chemical_units_of_measure
copy_maybe = tmo.utils.copy_maybe


# %%

# =============================================================================
# Representation
# =============================================================================

def component_identity(component, pretty=False):
    typeheader = f"{type(component).__name__}:"
    full_ID = f"{typeheader} {component.ID} (phase_ref={repr(component.phase_ref)})"
    phase = component.locked_state
    state = ' at ' + f"phase={repr(phase)}" if phase else ""
    return full_ID + state


# Will stored as an array when compiled
_num_component_properties = ('i_C', 'i_N', 'i_P', 'i_K', 'i_Mg', 'i_Ca',
                             'i_mass', 'i_charge',
                             'f_BOD5_COD', 'f_uBOD_COD', 'f_Vmass_Totmass', )

# Fields that cannot be left as None
_key_component_properties = (*_num_component_properties,
                             'particle_size', 'degradability', 'organic')

# All Component-related properties
_component_properties = (*_key_component_properties,
                         'measured_as', 'description', )
_component_slots = (*tmo.Chemical.__slots__,
                    *tuple('_'+i for i in _component_properties))

_checked_properties = (*_checked_properties, *_key_component_properties)

AbsoluteUnitsOfMeasure = tmo.units_of_measure.AbsoluteUnitsOfMeasure
component_units_of_measure = {
    'i_C': AbsoluteUnitsOfMeasure('g'), 
    'i_N': AbsoluteUnitsOfMeasure('g'), 
    'i_P': AbsoluteUnitsOfMeasure('g'), 
    'i_K': AbsoluteUnitsOfMeasure('g'), 
    'i_Mg': AbsoluteUnitsOfMeasure('g'), 
    'i_Ca': AbsoluteUnitsOfMeasure('g'), 
    'i_mass': AbsoluteUnitsOfMeasure('g'), 
    'i_charge': AbsoluteUnitsOfMeasure('mol')
    }


# %%

allowed_values = {
    'particle_size': ('Dissolved gas', 'Soluble', 'Colloidal', 'Particulate'),
    'degradability': ('Biological', 'Chemical', 'Undegradable'),
    'organic': (True, False)
    }

def check_return_property(name, value):
    if not value: return None
    elif name.startswith('i_') or name.startswith('f_'):
        try: return float(value)
        except: raise TypeError(f'{name} must be a number, not a {type(value).__name__}.')        
        if value>1 or value<0:
            raise ValueError(f'{name} must be within [0,1].')
    elif name in allowed_values.keys():
        assert value in allowed_values[name], \
            f'{name} must be in {allowed_values[name]}.'
        return value

# =============================================================================
# Define the Component class
# =============================================================================

class Component(tmo.Chemical):
    '''A subclass of the Chemical object in the thermosteam package with additional attributes and methods for waste treatment'''         

    __slots__ = _component_slots

    def __new__(cls, ID='', search_ID=None, formula=None, phase='l', measured_as=None, 
                i_C=None, i_N=None, i_P=None, i_K=None, i_Mg=None, i_Ca=None,
                i_mass=None, i_charge=None, f_BOD5_COD=None, f_uBOD_COD=None,
                f_Vmass_Totmass=None,
                description=None, particle_size=None,
                degradability=None, organic=None, **chemical_properties):
        
        if search_ID:
            self = super().__new__(cls, ID=ID, search_ID=search_ID,
                                   search_db=True, **chemical_properties)
        else:
            self = super().__new__(cls, ID=ID, search_db=False, **chemical_properties)

        self._ID = ID
        if formula:
            self.formula = formula
        tmo._chemical.lock_phase(self, phase)
        self.measured_as = measured_as
        self.i_C = i_C
        self.i_N = i_N
        self.i_P = i_P
        self.i_K = i_K
        self.i_Mg = i_Mg
        self.i_Ca = i_Ca
        self.i_mass = i_mass
        self.i_charge = i_charge        
        self.f_BOD5_COD = f_BOD5_COD
        self.f_uBOD_COD = f_uBOD_COD
        self.f_Vmass_Totmass = f_Vmass_Totmass                
        self.particle_size = particle_size
        self.degradability = degradability
        self.organic = organic
        self.description = description
        if not self.MW and not self.formula: self.MW = 1.
        return self

    @staticmethod
    def _atom_frac_setter(cmp, atom=None, frac=None):
        if cmp.formula:
            if frac:
                raise AttributeError('This Component has formula, '
                                     f'i_{atom} calculated based on formula, '
                                     'cannot be set.')
            else:
                if atom in cmp.atoms.keys():
                    return get_mass_frac(cmp.atoms)[atom]
                return 0. # does not have this atom
        else:
            return check_return_property(f'i_{atom}', frac)

    @property
    def i_C(self):
        '''
        [float] Carbon content of the Component, [g C/g measure unit].

        Notes
        -------
        [1] Must be within [0,1].
        [2] Will be calculated based on formula if given.
        '''
        return self._i_C or 0.
    @i_C.setter
    def i_C(self, i):
        self._i_C = self._atom_frac_setter(self, 'C', i)


    @property
    def i_N(self):
        '''
        [float] Nitrogen content of the Component, [g N/g measure unit].

        Notes
        -------
        [1] Must be within [0,1].
        [2] If the Component is measured as N, then i_N is 1.
        [3] Will be calculated based on formula if given.
        '''
        return self._i_N or 0.
    @i_N.setter
    def i_N(self, i):
        self._i_N = self._atom_frac_setter(self, 'N', i)

    @property
    def i_P(self):
        '''
        [float] Phosphorus content of the Component, [g P/g measure unit].

        Notes
        -------
        [1] Must be within [0,1].
        [2] If the Component is measured as P, then i_P is 1.
        [3] Will be calculated based on formula if given.
        '''
        return self._i_P or 0.
    @i_P.setter
    def i_P(self, i):
        self._i_P = self._atom_frac_setter(self, 'P', i)

    @property
    def i_K(self):
        '''
        [float] Potassium content of the Component, [g K/g measure unit].

        Notes
        -------
        [1] Must be within [0,1].
        [2] Will be calculated based on formula if given.
        '''
        return self._i_K or 0.
    @i_K.setter
    def i_K(self, i):
        self._i_K = self._atom_frac_setter(self, 'K', i)

    @property
    def i_Mg(self):
        '''
        [float] Magnesium content of the Component, [g Mg/g measure unit].

        Notes
        -------
        [1] Must be within [0,1].
        [2] Will be calculated based on formula if given.
        '''
        return self._i_Mg or 0.
    @i_Mg.setter
    def i_Mg(self, i):
        self._i_Mg = self._atom_frac_setter(self, 'Mg', i)
        
    @property
    def i_Ca(self):
        '''
        [float] Calcium content of the Component, [g Ca/g measure unit].

        Notes
        -------
        [1] Must be within [0,1].
        [2] Will be calculated based on formula if given.
        '''
        return self._i_Ca or 0.
    @i_Ca.setter
    def i_Ca(self, i):
        self._i_Ca = self._atom_frac_setter(self, 'Ca', i)

    @property
    def i_mass(self):
        '''[float] Mass content of the Component, [g Component/g measure unit].'''
        return self._i_mass or 1.
    @i_mass.setter
    def i_mass(self, i):
        self._i_mass = check_return_property('i_mass', i)
        
    @property
    def i_charge(self):
        '''
        [float] Charge content of the Component, [mol +/g measure unit].

        Notes
        -------
        Positive values indicate cations and negative values indicate anions.
        '''
        return self._i_charge or 0.
    @i_charge.setter
    def i_charge(self, i):
        self._i_charge = check_return_property('i_charge', i)

    @property
    def f_BOD5_COD(self):
        '''
        BOD5 fraction in COD of the Component, unitless.

        Notes
        -------
        [1] Must be within [0,1].
        [2] Must be smaller or equal to f_uBOD_COD.
        '''
        return self._f_BOD5_COD or 0.
    @f_BOD5_COD.setter
    def f_BOD5_COD(self, f):
        self._f_BOD5_COD = check_return_property('f_BOD5_COD', f)

    @property
    def f_uBOD_COD(self):
        '''
        [fload] Ultimate BOD fraction in COD of the Component, unitless.

        Notes
        -------
        [1] Must be within [0,1].
        [2] Must be larger or equal to f_BOD5_COD.
        '''
        return self._f_uBOD_COD or 0.
    @f_uBOD_COD.setter
    def f_uBOD_COD(self, f):
        frac = f or 0.
        if frac < self.f_BOD5_COD:
            raise ValueError('f_uBOD_COD cannot be less than f_BOD5_COD.')
        self._f_uBOD_COD = check_return_property('f_uBOD_COD', frac)

    @property
    def f_Vmass_Totmass(self):
        '''
        [fload] Volatile fraction of the mass of the Component, unitless.

        Notes
        -------
        Must be within [0,1].
        '''
        return self._f_Vmass_Totmass or 0.
    @f_Vmass_Totmass.setter
    def f_Vmass_Totmass(self, f):
        self._f_Vmass_Totmass = check_return_property('f_Vmass_Totmass', f)
        
    @property
    def description(self):
        '''[str] Description of the Component.'''
        return self._description
    @description.setter
    def description(self, description):
        self._description = description

    #!!! Do we need this? Why not just set the formula of this Component to be
    # the repsective element?
    @property
    def measured_as(self):
        '''
        [str] The unit as which the Component is measured.

        Notes
        -------
        Can be left as blank or chosen from 'COD', 'N', or 'P'.
        '''
        return self._measured_as
    @measured_as.setter
    def measured_as(self, measured_as):
        #!!! This will cause problems in calculating total mass
        # Might be better to create an 'i_COD' for this purpose
        if measured_as == 'COD':
            self._formula = 'O'
            self._MW = get_MW(self.atoms)
        elif measured_as == 'N':
            self._formula = 'N'
            self._MW = get_MW(self.atoms)
        elif measured_as == 'P':
            self._formula = 'P'
            self._MW = get_MW(self.atoms)
        self._measured_as = measured_as
        
    @property
    def particle_size(self):
        '''
        [str] Size of the Component based on the type.

        Notes
        -------
        Must be chosen from 'Dissolved gas', 'Soluble', 'Colloidal', or 'Particulate'.
        '''
        return self._particle_size
    @particle_size.setter
    def particle_size(self, particle_size):
        self._particle_size = check_return_property('particle_size', particle_size)

    @property
    def degradability(self):
        '''
        [str] Degradability of the Component.

        Notes
        -------
        Must be chosen from 'Biological', 'Chemical', or 'Undegradable'.
        '''
        return self._degradability
    @degradability.setter
    def degradability(self, degradability):
        self._degradability = check_return_property('degradability', degradability)

    @property
    def organic(self):
        '''[bool] True (organic) or False (inorganic)'''
        return self._organic
    @organic.setter
    def organic(self, organic):
        self._organic = bool(check_return_property('organic', organic))

    def show(self, chemical_info=False):
        '''
        Show Component properties.

        Parameters
        ----------
        chemical_info : [bool]
            Whether to show properties associated with the corresponding
            Chemical object of the Component. The default is False.
        '''
        info = ''
        if chemical_info:
            super().show()
        else:
            info = component_identity(self, pretty=True)
        info += '\nComponent-specific properties:\n'
        header = '[Others] '
        section = []
        for field in _component_properties:
            value = getattr(self, field)
            field = field.lstrip('_')
            if value is None:
                line = f"{field}: None"
            elif str(value) in ('True', 'False'):
                line = f"{field}: {value}" 
            else:
                if isinstance(value, (int, float)):
                    line = f"{field}: {value:.5g}"
                    units = component_units_of_measure.get(field, '')
                    if units: 
                        if field.startswith('i_'):
                            if self._measured_as: denom = self._measured_as
                            else: denom = ''
                            if field == 'i_charge': line += f' {units} +/g {denom}'
                            else: line += f' {units} {field[2:]}/g {denom}'
                        else: line += f' {units}'
                else:
                    value = str(value)
                    line = f"{field}: {value}"
                    if len(line) > 40: line = line[:40] + '...'
            section.append(line)
        info += header + ("\n" + 9*" ").join(section)
        print(info)
        
    _ipython_display_ = show

    def get_missing_properties(self, properties=None):
        missing = []
        for i in (properties or _checked_properties):
            if getattr(self, i) == 0:
                continue
            elif str(getattr(self, i)) in ('True', 'False'):
                continue
            elif not getattr(self, i):
                missing.append(i)
        return missing

    def copy(self, ID, **data):
        new = self.__class__.__new__(cls=self.__class__, ID=ID)

        for field in self.__slots__:
            if field == '_CAS': continue
            value = getattr(self, field)
            setattr(new, field, copy_maybe(value))
        new._ID = ID
        new._locked_state = self._locked_state
        new._init_energies(new.Cn, new.Hvap, new.Psat, new.Hfus, new.Sfus, new.Tm,
                           new.Tb, new.eos, new.eos_1atm, new.phase_ref)
        new._label_handles()
        for i,j in data.items(): setattr(new, i , j)
        return new
    __copy__ = copy

    @classmethod
    def from_chemical(cls, ID, chemical, phase='l', measured_as=None, 
                      i_C=None, i_N=None, i_P=None, i_K=None, i_Mg=None, i_Ca=None,
                      i_mass=None, i_charge=None, f_BOD5_COD=None, f_uBOD_COD=None,
                      f_Vmass_Totmass=None, description=None, 
                      particle_size=None, degradability=None, organic=None, 
                      **data):
        '''Return a new Component from Chemical'''
        new = cls.__new__(cls, ID=ID, phase=phase)
        for field in chemical.__slots__:
            value = getattr(chemical, field)
            setattr(new, field, copy_maybe(value))
        new._ID = ID
        new._locked_state = phase
        new._init_energies(new.Cn, new.Hvap, new.Psat, new.Hfus, new.Sfus, new.Tm,
                           new.Tb, new.eos, new.eos_1atm, new.phase_ref)
        new._label_handles()
        new.measured_as = measured_as        
        new.i_C = i_C
        new.i_N = i_N
        new.i_P = i_P
        new.i_K = i_K
        new.i_Mg = i_Mg
        new.i_Ca = i_Ca
        new.i_mass = i_mass
        new.i_charge = i_charge
        new.f_BOD5_COD = f_BOD5_COD
        new.f_uBOD_COD = f_uBOD_COD
        new.f_Vmass_Totmass = f_Vmass_Totmass
        new.description = description
        new.particle_size = particle_size
        new.degradability = degradability
        new.organic = organic
        
        for i,j in data.items(): setattr(new, i , j)
        return new


















